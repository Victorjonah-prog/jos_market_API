from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import List,Dict,Optional


app = FastAPI(title="jos market API")



class Vendor(BaseModel):
    id: Optional[int] = None
    name: str
    market_location: str
    phone: str
    created_at: datetime

class Produce(BaseModel):
    id: int
    vendor_id: int
    name: str
    quantity_kg: float
    price_per_kg: float
    category: str
    is_available: bool

class VendorWithProduce(Vendor):
    produces: List["Produce"] = []


class VendorCreate(BaseModel):
    name: str
    market_location: str
    phone: str
    created_at: datetime

class Order(BaseModel):
    id: int
    produce_id: int
    buyer_name: str
    buyer_phone: str
    produce_name: str
    quantity_kg: float
    total_price: float
    delivery_area: str
    status: str
    order_date: datetime

class MarketDB:
    def __init__(self):
        self.vendors:Dict[int, Vendor] = {}
        self.produces:Dict [int, Produce] = {}
        self.orders:Dict[int, Order]= {}
        self.vendor_id_counter = 1
        self.produce_id_counter =1
        self.order_id_counter = 1
    
    def add_vendor(self, vendor: Vendor):
        vendor.id= self.vendor_id_counter
        self.vendors[self.vendor_id_counter]= vendor
        self.vendor_id_counter +=1
        return vendor

    def increment_vendor_id(self):
        self.vendor_id_counter +=1
        return self.vendor_id_counter

    def get_all_vendors(self) -> List[Vendor]:
        return list(self.vendors.values())
    
    def get_vendor_with_produces(self, vendor_id: int):
        vendor = self.vendors.get(vendor_id)
        if not vendor:
            return None
        produces = [p for p in self.produces.values() if p.vendor_id == vendor_id]
        return VendorWithProduce(**vendor.dict(), produces=produces)
    
    
    def update_vendor_info(self, vendor_id:int, name: str, market_location: str, phone: str):
        vendor= self.vendors.get(vendor_id)
        if not vendor:
            return None
        vendor.name = name
        vendor.market_location = market_location
        vendor.phone = phone
        self.vendors[vendor_id] = vendor
        return vendor
    
    def remove_vendor(self, vendor_id:int):
        if vendor_id in self.vendors:
            del self.vendors[vendor_id]
            return True
        return False
    



    def add_produce(self, produce: Produce):
        produce.id = self.produce_id_counter
        self.produces[self.produce_id_counter]= produce
        self.produce_id_counter +=1

    def get_specific_produce_details(self, produce_id:int):
        return self.produces.get(produce_id)
    

    

    def add_order(self, order: Order):
        order.id = self.order_id_counter
        self.orders[self.order_id_counter]= order
        self.order_id_counter +=1

    def get_order_details(self, order_id:int):
        return self.orders.get(order_id)
    



db_instance = MarketDB()

# endpoints
@app.post("/vendors")
def Register_vendor(vendor: Vendor):
    db_instance.add_vendor(vendor)
    if not vendor:
        raise HTTPException(status_code=400, detail="vendor registration failed")
    return {
        "message": "vendor registered successfully",
        "vendor": vendor

    }

@app.get("/vendors/")
def get_all_vendors():
    vendors=db_instance.get_all_vendors()
    return {
        
        "message": "vendors retrieved successfully",
        "vendors": vendors
    }

@app.get("/vendors/{vendor_id}")
def get_vendor(vendor_id: int) -> VendorWithProduce:
    vendor= db_instance.get_vendor_with_produces(vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="vendor does not exist")
    return vendor

@app.put("/vendors/{vendor_id}")
def update_vendor(vendor_id:int, name:str, market_location:str, phone:str):
    vendor= db_instance.update_vendor_info(vendor_id,name, market_location, phone)
    if not vendor:
        raise HTTPException(status_code=404, detail= "vendor does not eist")
    return {
        "message": "vendor updated successfully",
        "vendor": vendor
    }

@app.post("/produce")
def add_produce(produce: Produce):
    db_instance.add_produce(produce)
    if not produce:
        raise HTTPException(status_code=400, detail="adding produce failed")
    return {
        "message": "produce added successfully",
        "produce": produce
    }

@app.get("/produce/{produce_id}")
def get_produce(produce_id:int):
    produce= db_instance.get_specific_produce_details(produce_id)
    if not produce:
        raise HTTPException(status_code=404, detail="produce does not exist")
    return produce  

@app.post("/orders")
def place_order(order: Order):
    db_instance.add_order(order)
    if not order:
        raise HTTPException(status_code=400, detail="placing order failed")
    return {
        "message": "order placed successfully",
        "order": order
    } 

@app.get("/orders/{order_id}")
def get_order(order_id:int):
    order= db_instance.get_order_details(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="order does not exist")
    return order
 





