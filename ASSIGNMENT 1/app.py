from fastapi import FastAPI,Query
app=FastAPI()
#temp database
products = [
    {'id': 1, 'name': 'Wireless Mouse', 'price': 499,  'category': 'Electronics', 'instock': True },
    {'id': 2, 'name': 'Notebook',       'price':  99,  'category': 'Stationery',  'instock': True },
    {'id': 3, 'name': 'USB Hub',         'price': 799, 'category': 'Electronics', 'instock': False},
    {'id': 4, 'name': 'Pen Set',          'price':  49, 'category': 'Stationery',  'instock': True },
    {"id": 5, "name": "Laptop Stand", "price": 1299, "category": "Electronics", "instock": True}, 
    {"id": 6, "name": "Mechanical Keyboard", "price": 2499, "category": "Electronics", "instock": True}, 
    {"id": 7, "name": "Webcam", "price": 1899, "category": "Electronics", "instock": False},
]
@app.get('/')
def home():
    return {'message':'Welcome to our E-commerce API!'}
@app.get('/products')
def get_all_products():
    return {'products': products, 'total': len(products)}
# 1
@app.get('/products/filter')
def filter_products(
    category:str=Query(None,description='Electronics or Stationary'),
    max_price:int=Query(None,description='Max price'),
    instock:bool=Query(None,description='True=in stock only')
):
    result=products
    if category:
        result=[p for p in result if p['category']==category]
    if max_price:
        result=[p for p in result if p['price']<=max_price]
    if instock is not None:
        result=[p for p in result if p['instock']==instock]
    return {'filtered_products':result, 'count':len(result)}
# 2
@app.get("/products/category/{category_name}") 
def get_by_category(category_name:str): 
    result=[p for p in products if p["category"]==category_name] 
    if not result: 
        return {"error":"No products found in this category"} 
    return {"category":category_name, "products":result, "total":len(result)}
# 3
@app.get("/products/instock") 
def get_instock(): 
    available=[p for p in products if p["instock"]==True] 
    return {"in_stock_products":available, "count":len(available)}
# 4
@app.get("/store/summary")
def store_summary():
    in_stock_count=len([p for p in products if p["instock"]])
    out_stock_count=len(products)-in_stock_count
    categories=list(set([p["category"] for p in products]))
    return {"store_name": "My E-commerce Store","total_products": len(products),"in_stock": in_stock_count,"out_of_stock": out_stock_count,"categories": categories}
# 5
@app.get("/products/search/{keyword}")
def search_products(keyword:str):
    result=[p for p in products if keyword.lower() in p["name"].lower()]
    if not result:
        return {"error":"No products found with this keyword"}
    return {"keyword":keyword, "products":result, "total":len(result)}
# bonus
@app.get("/products/deals")
def get_deals():
    cheapest=min(products,key=lambda p:p["price"])
    expensive=max(products,key=lambda p:p["price"])
    return {"best_deal": cheapest,"premium_pick":expensive,}
