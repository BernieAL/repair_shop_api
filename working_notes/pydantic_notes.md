
api -> models -> schema 


--------------------------



Pydantic 

pydantic Schemas

Db models are given by sqlalchemy - these represent data IN the DB

now we need schemas that represent data in/out of the API - these are given by pydantic

# API Schema (Pydantic) - what users see/send
class CustomerResponse(BaseModel):
    id: int
    name: str
    email: str
    # No password_hash!
    # No created_at if you don't want to expose it

pydantic defines the contract for each api endpoint of
the data thats expected in/out. it defines the transaction template for what data flwos in and out of API endpoints

    The Perfect Mental Model
        Think of each endpoint as having:

            Input contract (what the user must send)
            Output contract (what the API promises to return)

            Pydantic enforces both sides.

    ✅ What data comes IN (validation, required fields)
    ✅ What data goes OUT (serialization, field filtering)
    ✅ Documentation (auto-generated)
    ✅ Type safety (IDE autocomplete, runtime checks)

w/o pydantic
    we need to manually validate data for each field
    and repeat alot of boilerplate

    40+ lines of boilerplate
    Manual validation for every field
    Easy to forget validation
    No automatic documentation
    No type hints (IDE can't help)
    Brittle - typos like "emal" won't be caught
    Manual JSON serialization
    DateTime serialization you have to handle

with pydantic

    15 lines (vs 40+)
    All validation automatic
    Type safety
    Auto-generated docs
    Auto JSON serialization
    IDE autocomplete


--------------------------
WHY 3 schemas per model?

    base - common fields shared across schemas

    create - what users send when creating 

    update - all firlds optional since partial updates allowed

    response - what api returns

-----------------------------

