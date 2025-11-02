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
    

    def update_produce_item(self, produce_id:int, name:str, quantity_kg: float, price_per_kg: float, category:str, is_available: bool):
        produce= self.produces.get(produce_id)
        if not produce:
            return None
        produce.name = name
        produce.quantity_kg = quantity_kg
        produce.price_per_kg = price_per_kg
        produce.category = category
        produce.is_available = is_available
        self.produces[produce_id] = produce
        return produce
    
    def update_quantity_available(self, produce_id:int, quantity_kg: float):
        produce = self.produces.get(produce_id)
        if not produce:
            return None
        produce.quantity_kg = quantity_kg
        self.produces[produce_id] = produce
        return produce
    

    

    def add_order(self, order: Order):
        order.id = self.order_id_counter
        self.orders[self.order_id_counter]= order
        self.order_id_counter +=1

    def get_order_details(self, order_id:int):
        return self.orders.get(order_id)

    def update_order_status(self, order_id: int, status: str):
        order = self.orders.get(order_id)
        if not order:
            return None
        order.status= status
        self.orders[order_id] = order
        return order
    
    def cancel_order(self, order_id: int):
        order =self.orders.get(order_id)
        if not order:
            return None
        order.status = "cancelled"
        self.orders[order_id] = order
        return order
    

    



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


@app.put("/produce/{produce_id}")
def update_produce(produce_id:int, name: str, quantity_kg: float, price_per_kg: float, category:str, is_available: bool):
    produce = db_instance.update_produce_item(produce_id, name, quantity_kg, price_per_kg, category, is_available)
    if not produce:
        raise HTTPException(status_code=404, detail="produce does not exist")
    return {
        "message": "produce updated successfully",
        "produce": produce
    }

@app.patch("/produce/{produce_id}/quantity")
def update_produce_quantity(produce_id:int, quantity_kg: float):
    produce = db_instance.update_quantity_available(produce_id, quantity_kg)
    if not produce:
        raise HTTPException(status_code=404, detail="produce does not exist")
    return {

        "message": "produce quantity updated successfully",
        "produce": produce
    }

@app.patch("/orders/{order_id}/status")
def update_order_status(order_id:int, status: str):
    order = db_instance.update_order_status(order_id, status)
    if not order:
        raise HTTPException(status_code=404, detail="order does not exist")
    return {
        "message": "order status updated successfully",
        "order": order
    }


@app.delete("/vendors/{vendor_id}")
def delete_vendor(vendor_id:int):
    success= db_instance.remove_vendor(vendor_id)
    if not success:
        raise HTTPException(status_code=404, detail="vendor does not exist")
    return {
        "message": "vendor deleted successfully"
    }


@app.delete("/orders/{order_id}")
def cancel_order(order_id:int):
    order = db_instance.cancel_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="order does not exist")
    return {
        "message": "order cancelled successfully",
        "order": order
    }



 





