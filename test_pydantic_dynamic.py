from pydantic import create_model, Field
from typing import Optional

def main():
    print("Testing dynamic Pydantic model creation...")
    try:
        fields = {
            "username": (str, Field(description="The username")),
            "age": (Optional[int], Field(default=None, description="The age"))
        }
        MyModel = create_model("MyModel", **fields)
        print("Model created successfully.")
        print(MyModel.schema())
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
