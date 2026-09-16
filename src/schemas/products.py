from pydantic import BaseModel, ConfigDict, Field


class ProductResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    product_id: str = Field(alias="_id")
    product_category_name: str | None = None
    product_category_name_english: str | None = None
    product_name_lenght: int | None = None
    product_description_lenght: int | None = None
    product_photos_qty: int | None = None
    product_weight_g: float | None = None
    product_length_cm: float | None = None
    product_height_cm: float | None = None
    product_width_cm: float | None = None
