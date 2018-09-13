# flask-quiz

## Install
```
pip install -r requirements.txt
```

## Run

### Production
```
flask run
```

### Development
```
export FLASK_ENV=development
flask run
```
or
```
flask run --reload --debugger
```

## Routes
```
# available
/                 # redirect to login
/index            # redirect to login
/auth/login       # login page
/auth/logout      # logout, redirect to login
/quiz             # quiz menu
/quiz/{quiz}/{#}  # quiz question #

# future release
/quiz/{quiz}      # instructions for {quiz}
/import           # quiz import form
/user             # user management
/user/{user}      # statistics for {user}
```

## Phases
Phase | Hours | Status
:--- | ---: | ---
Flask page with sample data & score tracking | 5 | :heavy_check_mark:
Simple Excel-driven quiz | <del>3</del> 2 | :heavy_check_mark:
Percentage points off | <del>3</del> 2 |
Directory-based Quiz selection | <del>2</del> 0 | :heavy_check_mark:
Database-driven quiz history | <del>4</del> 6 |
Material Design-based GUI | 5 |
**Total** | **<del>22</del> 20**

### Flask page with sample data & score tracking
The website engine is driven by the Flask microframework. Hard-coded sample data will be converted to questions dynamically on page load, and sessions will be used to track answers and scores.

### Simple Excel-driven quiz
This phase adds the ability to import Excel files as quiz data.

### Percentage points off
This phase adds the mathematical logic for determining the percentage off the guess was from the correct answer, and incorporating it into the score.

### Directory-based Quiz selection
A menu page will be added to select from a list of Excel files found in a specified folder. After database integration, this will be used for importing Excel data as quizzes to be saved.

### Database-driven quiz history
Database functionality includes storing user info, including previous test scores, as well as saving imported quiz data.

### Material Design-based GUI
This phase will convert the text-based, simple web page to having dynamic elements, custom buttons, and a consistent style throughout all pages.
 