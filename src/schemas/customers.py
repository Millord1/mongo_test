from pydantic import BaseModel, ConfigDict, Field


class CustomerResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    customer_id: str = Field(alias="_id")
    customer_unique_id: str
    customer_zip_code_prefix: int
    customer_city: str
    customer_state: str
