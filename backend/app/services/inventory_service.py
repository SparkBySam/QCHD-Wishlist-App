from sqlalchemy.orm import Session

from app.models import InventoryItem
from app.scraper import ScrapedBike, run_scraper


def sync_inventory(db: Session) -> dict:
    """
    Run the scraper and reconcile results with the InventoryItem table.

    - Insert new stock numbers
    - Reactivate previously inactive items that reappear
    - Mark stock numbers missing from the scrape as inactive
    """
    scraped: list[ScrapedBike] = run_scraper()
    scraped_by_stock = {bike.stock_number: bike for bike in scraped}
    scraped_stock_numbers = set(scraped_by_stock.keys())

    existing_items = db.query(InventoryItem).all()
    existing_by_stock = {item.stock_number: item for item in existing_items}
    existing_stock_numbers = set(existing_by_stock.keys())

    new_items = 0
    reactivated_items = 0
    deactivated_items = 0
    newly_active_ids: list[int] = []

    for stock_number, bike in scraped_by_stock.items():
        if stock_number not in existing_by_stock:
            item = InventoryItem(
                stock_number=bike.stock_number,
                model_name=bike.model_name,
                year=bike.year,
                color=bike.color or "",
                condition=bike.condition or "unknown",
                is_active=True,
            )
            db.add(item)
            db.flush()
            newly_active_ids.append(item.id)
            new_items += 1
        else:
            item = existing_by_stock[stock_number]
            was_inactive = not item.is_active
            item.model_name = bike.model_name
            item.year = bike.year
            item.color = bike.color or ""
            item.condition = bike.condition or "unknown"
            item.is_active = True
            if was_inactive:
                reactivated_items += 1
                newly_active_ids.append(item.id)

    for stock_number in existing_stock_numbers - scraped_stock_numbers:
        item = existing_by_stock[stock_number]
        if item.is_active:
            item.is_active = False
            deactivated_items += 1

    db.commit()

    return {
        "scraped_count": len(scraped),
        "new_items": new_items,
        "reactivated_items": reactivated_items,
        "deactivated_items": deactivated_items,
        "newly_active_ids": newly_active_ids,
    }
