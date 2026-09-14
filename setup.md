Here’s a clean README you can use:

 README

# Project Setup

 Follow the steps below to set up the project locally.

## 1\. Create a Virtual Environment

 Create a virtual environment using `uv`:

```
uv venv
```

## 2\. Activate the Virtual Environment

 On Windows:

```
.venv\Scripts\activate
```

## 3\. Create the Project Structure

 Run the following command to generate the project structure:

```
python create_project.py
```

## 4\. Create `__init__.py` Files

 Create `__init__.py` files in the required package/constructor directories so that Python recognizes them as packages.

## 5\. Install Dependencies

 Install the project dependencies using:

```
uv pip install -r requirements.txt
```

## Complete Setup

 You can run the commands in the following order:

```
uv venv
.venv\Scripts\activate
python create_project.py
uv pip install -r requirements.txt
```
