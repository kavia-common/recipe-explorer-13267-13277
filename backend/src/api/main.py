from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List, Optional
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from src.api.models import (
    SessionLocal,
    init_db,
    User,
    Recipe,
)
from src.api.schemas import (
    RecipeRead,
    RecipeCreate,
    UserCreate,
    UserRead,
)

app = FastAPI(
    title="Recipe Explorer Backend API",
    description="API for browsing, searching, and saving favorite recipes.",
    version="1.0.0",
    openapi_tags=[
        {"name": "Recipes", "description": "Operations with recipes"},
        {"name": "Favorites", "description": "Operations with favorite recipes"},
        {"name": "Users", "description": "User registration and login"},
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Auth token dependency (optional, basic structure)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize database if not exists
init_db()

# ========================================================================
# Utility Functions
# ========================================================================

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

# ========================================================================
#                Public API Endpoints for the Recipe App
# ========================================================================

@app.get("/", tags=["Recipes"])
def health_check():
    """Health check endpoint."""
    return {"message": "Healthy"}

# PUBLIC_INTERFACE
@app.get("/recipes", response_model=List[RecipeRead], tags=["Recipes"], summary="List/Search recipes")
def list_or_search_recipes(
    q: Optional[str] = Query(None, description="Search query"),
    category: Optional[str] = Query(None, description="Filter by category"),
    db: Session = Depends(get_db),
):
    """
    Returns a list of recipes, optionally filtered by search query and/or category.
    """
    query = db.query(Recipe)
    if q:
        query = query.filter(Recipe.title.ilike(f"%{q}%"))
    if category:
        query = query.filter(Recipe.category == category)
    recipes = query.order_by(Recipe.id.desc()).all()
    return recipes

# PUBLIC_INTERFACE
@app.get("/recipes/{recipe_id}", response_model=RecipeRead, tags=["Recipes"], summary="Get recipe by ID")
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """
    Returns the details for a single recipe by ID.
    """
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe

# PUBLIC_INTERFACE
@app.post("/recipes", response_model=RecipeRead, status_code=201, tags=["Recipes"], summary="Create recipe")
def create_recipe(recipe: RecipeCreate, db: Session = Depends(get_db)):
    """
    (Demo endpoint) Create a new recipe.
    """
    db_recipe = Recipe(**recipe.dict())
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    return db_recipe

# (Optionally add update/delete endpoints for recipe management)

# --------- User Registration/Login Endpoints (Optional for MVP) ------------

@app.post("/register", response_model=UserRead, tags=["Users"], summary="Register new user")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new user.
    """
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_pw = get_password_hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# (Simple demo: No JWT issued, token stub, not for prod!)
@app.post("/token", tags=["Users"], summary="Login to get access token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticates user and returns a stub access token. (Replace with real JWT for production)
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    # NOTE: In production generate JWT token
    return {
        "access_token": user.username + "-token-demo",
        "token_type": "bearer",
    }

# ---------- Favorites Endpoints ---------------

# PUBLIC_INTERFACE
@app.post("/favorites/{recipe_id}", tags=["Favorites"], summary="Add recipe to favorites")
def add_to_favorites(
    recipe_id: int,
    user_id: int = Query(..., description="User ID for favorites"),
    db: Session = Depends(get_db)
):
    """
    Save a recipe as a favorite for the given user.
    """
    user = db.query(User).filter(User.id == user_id).first()
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not user or not recipe:
        raise HTTPException(status_code=404, detail="User or Recipe not found")
    if recipe in user.favorites:
        return {"message": "Already favorited"}
    user.favorites.append(recipe)
    db.commit()
    return {"message": "Recipe added to favorites"}

# PUBLIC_INTERFACE
@app.delete("/favorites/{recipe_id}", tags=["Favorites"], summary="Remove recipe from favorites")
def remove_from_favorites(
    recipe_id: int,
    user_id: int = Query(..., description="User ID for favorites"),
    db: Session = Depends(get_db)
):
    """
    Remove a recipe from favorites for the given user.
    """
    user = db.query(User).filter(User.id == user_id).first()
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not user or not recipe:
        raise HTTPException(status_code=404, detail="User or Recipe not found")
    if recipe in user.favorites:
        user.favorites.remove(recipe)
        db.commit()
        return {"message": "Recipe removed from favorites"}
    return {"message": "Recipe not in favorites"}

# PUBLIC_INTERFACE
@app.get("/users/{user_id}/favorites", response_model=List[RecipeRead], tags=["Favorites"], summary="Get user's favorite recipes")
def get_favorites(user_id: int, db: Session = Depends(get_db)):
    """
    Get the list of favorite recipes for the given user.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.favorites
