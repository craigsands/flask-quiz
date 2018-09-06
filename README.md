# flask-quiz

## Run
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
/                 # main menu/ select a quiz
/quiz             # quiz menu
/quiz/{quiz}      # instructions for {quiz}
/quiz/{quiz}/{#}  # quiz question #
/import           # quiz import form
/user             # user management
/user/{user}      # statistics for {user}
```

## Phases
Phase | Hours
:--- | ---:
Flask page with sample data & score tracking | 5
Simple Excel-driven quiz | 3
Percentage points off | 3
Directory-based Quiz selection | 2
Database-driven quiz history | 4
Material Design-based GUI | 5
**Total** | **22**
