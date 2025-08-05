from pydantic import BaseModel, Field
from typing import Optional

# PUBLIC_INTERFACE
class RecipeBase(BaseModel):
    title: str = Field(..., description="The title of the recipe")
    description: Optional[str] = Field(None, description="A short description")
    ingredients: Optional[str] = Field(None, description="Ingredients list")
    instructions: Optional[str] = Field(None, description="Preparation instructions")
    image_url: Optional[str] = Field(None, description="Image URL")
    category: Optional[str] = Field(None, description="Recipe category")

# PUBLIC_INTERFACE
class RecipeCreate(RecipeBase):
    pass

# PUBLIC_INTERFACE
class RecipeRead(RecipeBase):
    id: int

    class Config:
        orm_mode = True

# PUBLIC_INTERFACE
class UserBase(BaseModel):
    username: str = Field(..., description="Username")

# PUBLIC_INTERFACE
class UserCreate(UserBase):
    password: str = Field(..., description="Password")

# PUBLIC_INTERFACE
class UserRead(UserBase):
    id: int

    class Config:
        orm_mode = True

# PUBLIC_INTERFACE
class FavoriteRead(BaseModel):
    recipe: RecipeRead

    class Config:
        orm_mode = True

# PUBLIC_INTERFACE
class Token(BaseModel):
    access_token: str
    token_type: str
