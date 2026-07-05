from sqlalchemy.orm import Session

from app.schemas import ScrapeResult
from app.services.app_state_service import set_scrape_error, set_scrape_running, set_scrape_success
from app.services.inventory_service import sync_inventory
from app.services.matching_service import run_matching


def run_scrape_and_match(db: Session) -> ScrapeResult:
    set_scrape_running(db, "Scraping dealership inventory…")

    try:
        inventory_result = sync_inventory(db)
        new_matches = run_matching(
            db, inventory_item_ids=inventory_result["newly_active_ids"]
        )

        result = ScrapeResult(
            scraped_count=inventory_result["scraped_count"],
            new_items=inventory_result["new_items"],
            reactivated_items=inventory_result["reactivated_items"],
            deactivated_items=inventory_result["deactivated_items"],
            new_matches=new_matches,
            message=(
                f"Scraped {inventory_result['scraped_count']} bikes: "
                f"{inventory_result['new_items']} new, "
                f"{inventory_result['reactivated_items']} reactivated, "
                f"{inventory_result['deactivated_items']} deactivated, "
                f"{new_matches} new matches."
            ),
        )
        set_scrape_success(db, result.message)
        return result
    except Exception as exc:
        set_scrape_error(db, str(exc))
        raise
