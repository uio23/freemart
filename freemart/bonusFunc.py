# Importing 3rd party components
import statistics as stats

# Importing freemart components
from .models import Product, User

from .helperFunc import removeOutliers


def calcSaleBonus(user: User) -> int:
    saleBonus = 0

    if user.sale_count <6 :
        items = Product.query.filter(Product.listed==True, Product.username != user.username).all()

        # If there is nothing selling, calculate the avg price from all products
        prices = [item.price for item in items]
        if not items:
            items = Product.query.filter(Product.username != user.username).all()
            if not items:
                prices = [0]
        priceAvg = stats.mean(removeOutliers(prices))
        saleBonus = int((priceAvg/3))
    return saleBonus
