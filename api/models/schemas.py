# Serializers :- helper function to convert MongoDB document to  dictionary
def convert_individual_book(book): # Not used - pydantic used instead
    return {
        "id": str(book["_id"]),
        "name": book.get("name"),
        "description": book.get("description"),
        "category": book.get("category"),
        "price_with_tax": book.get("price_with_tax"),
        "price_without_tax": book.get("price_without_tax"),
        "availability": book.get("availability"),
        "review": book.get("review"),
        "cover_image_url": book.get("cover_image_url"),
        "rating": book.get("rating"),
    }
    
def convert_all_books(books): # Not used - pydantic used instead
    return {
        "books": [book["name"] for book in books if "name" in book]
    }

def convert_all_change_logs(logs): # used
    if not logs:
        return {"error": "No data found"}

    return {
        "changes": [
            {
                "name": log.get("name"),
                "changes": log.get("changes")
            }
            for log in logs if "name" in log
        ]
    }
