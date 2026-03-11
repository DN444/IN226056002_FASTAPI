from fastapi import FastAPI,Query,HTTPException
from pydantic import BaseModel,Field,EmailStr
from typing import Optional,List
app=FastAPI()
#temp database
products = [
    {'id':1,'name':'Wireless Mouse','price':499,'category':'Electronics','instock':True},
    {'id':2,'name':'Notebook','price':99, 'category':'Stationery','instock':True},
    {'id':3,'name':'USB Hub','price':799,'category':'Electronics','instock':False},
    {'id':4,'name':'Pen Set','price':49,'category':'Stationery','instock':True}
]
orders=[]
feedback=[]
order_counter=1
def find_product(product_id:int):
    return next((p for p in products if p['id']==product_id),None)
@app.get('/')
def home():
    return {'message':'Welcome to our E-commerce API!'}
@app.get('/products')
def get_all_products():
    return {'products':products,'total':len(products)}
# 1
@app.get('/products/filter')
def filter_products(
    category:str=Query(None),
    min_price:int=Query(None),
    max_price:int=Query(None),
    in_stock:bool=Query(None),
):
    result=products
    if category:result=[p for p in result if p['category']== category]
    if min_price:result=[p for p in result if p['price']>=min_price]
    if max_price:result=[p for p in result if p['price']<=max_price]
    if in_stock is not None:result=[p for p in result if p['in_stock']==in_stock]
    return {'filtered_products':result,'count':len(result)}
# 2
@app.get('/products/{product_id}')
def get_product(product_id:int):
    product=find_product(product_id)
    if not product:
        return {'error':'Product not found'}
    return {'product':product}
@app.get("/products/{product_id}/price")
def get_product_price(product_id: int):
    product=find_product(product_id)
    if product:
        return {"name":product["name"],"price":product["price"]}
    return {"error":"Product not found"}
# 3
class CustomerFeedback(BaseModel):
    customer_name:str=Field(...,min_length=2,max_length=100)
    product_id:int=Field(...,gt=0)
    rating:int=Field(...,ge=1,le=5)
    comment:Optional[str]=Field(None,max_length=300)
@app.post("/feedback")
def submit_feedback(data: CustomerFeedback):
    feedback.append(data.dict())
    return {"message": "Feedback submitted successfully", "total_feedback": len(feedback)}
# 4
@app.get('/products/summary')
def product_summary():
    in_stock=[p for p in products if p["in_stock"]]
    out_stock=[p for p in products if not p["in_stock"]]
    expensive=max(products,key=lambda p:p["price"])
    cheapest=min(products,key=lambda p:p["price"])
    categories=list(set(p["category"] for p in products))
    return {
        "total_products":len(products),
        "in_stock_count":len(in_stock),
        "out_of_stock_count":len(out_stock),
        "most_expensive":{"name":expensive["name"],"price":expensive["price"]},
        "cheapest":{"name":cheapest["name"],"price":cheapest["price"]},
        "categories":categories,
    }
# 5 and bonus
class OrderItem(BaseModel):
    product_id:int=Field(...,gt=0)
    quantity:int=Field(...,gt=0,le=50)
class BulkOrder(BaseModel):
    company_name:str=Field(...,min_length=2)
    contact_email:EmailStr
    items:List[OrderItem]=Field(...,min_items=1)
class OrderRequest(BaseModel):
    customer_name:str=Field(...,min_length=2,max_length=100)
    product_id:int=Field(...,gt=0)
    quantity:int=Field(...,gt=0,le=100)
    delivery_address:str=Field(...,min_length=10)
@app.post('/orders')
def place_order(order_data:OrderRequest):
    global order_counter
    product=find_product(order_data.product_id)
    if not product:return {'error':'Product not found'}
    if not product['in_stock']:return {'error':f"{product['name']} is out of stock"}
    order={
        'order_id':order_counter,
        'customer_name':order_data.customer_name,
        'product':product['name'],
        'quantity':order_data.quantity,
        'total_price':product['price']*order_data.quantity,
        'status':'confirmed'
    }
    orders.append(order)
    order_counter+=1
    return {'message':'Order placed successfully','order':order}
@app.post("/orders/bulk")
def place_bulk_order(order:BulkOrder):
    confirmed,failed,grand_total=[],[],0
    for item in order.items:
        product=find_product(item.product_id)
        if not product:
            failed.append({"product_id":item.product_id,"reason":"Not found"})
        elif not product["in_stock"]:
            failed.append({"product_id":item.product_id,"reason":"Out of stock"})
        else:
            subtotal=product["price"]*item.quantity
            grand_total+=subtotal
            confirmed.append({"product":product["name"],"qty":item.quantity,"subtotal":subtotal})
    return {"company":order.company_name,"confirmed":confirmed,"failed":failed,"grand_total":grand_total}
@app.get('/orders')
def get_all_orders():
    return {'orders':orders,'total_orders':len(orders)}