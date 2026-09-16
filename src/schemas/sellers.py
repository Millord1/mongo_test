from pydantic import BaseModel, ConfigDict, Field


class SellerResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    seller_id: str = Field(alias="_id")
    seller_zip_code_prefix: int
    seller_city: str
    seller_state: str
