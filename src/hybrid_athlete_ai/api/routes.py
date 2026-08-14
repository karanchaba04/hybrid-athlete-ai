from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from hybrid_athlete_ai.database import get_db
from hybrid_athlete_ai.models.goal import Goal, GoalCreate, GoalUpdate
from hybrid_athlete_ai.schemas.quick import QuickWorkoutCreate
from hybrid_athlete_ai.schemas.training import (
    PersonalRecord,
    TrainingSessionCreate,
    TrainingSessionRead,
    WeeklyVolume,
)
from hybrid_athlete_ai.services import workout_service


router = APIRouter()


@router.post("/workouts", response_model=TrainingSessionRead, status_code=201)
def create_workout(payload: TrainingSessionCreate, db: Session = Depends(get_db)):
    return workout_service.create_workout(db, payload)


@router.post("/workouts/quick", response_model=TrainingSessionRead, status_code=201)
def create_quick_workout(payload: QuickWorkoutCreate, db: Session = Depends(get_db)):
    return workout_service.create_quick_workout(db, payload)


@router.get("/workouts", response_model=list[TrainingSessionRead])
def list_workouts(
    start_date: date | None = None,
    end_date: date | None = None,
    session_type: str | None = None,
    limit: int = Query(default=50, le=200),
    db: Session = Depends(get_db),
):
    return workout_service.list_workouts(
        db,
        start_date=start_date,
        end_date=end_date,
        session_type=session_type,
        limit=limit,
    )


@router.get("/workouts/{workout_id}", response_model=TrainingSessionRead)
def get_workout(workout_id: int, db: Session = Depends(get_db)):
    workout = workout_service.get_workout(db, workout_id)
    if workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    return workout


@router.get("/analytics/prs", response_model=list[PersonalRecord])
def get_personal_records(
    exercise_name: str | None = None,
    db: Session = Depends(get_db),
):
    return workout_service.get_personal_records(db, exercise_name=exercise_name)


@router.get("/analytics/weekly-volume", response_model=WeeklyVolume)
def get_weekly_volume(
    reference_date: date | None = None,
    db: Session = Depends(get_db),
):
    return workout_service.get_weekly_volume(db, reference_date=reference_date)


@router.post("/goals", response_model=Goal, status_code=201)
def create_goal(payload: GoalCreate, db: Session = Depends(get_db)):
    return workout_service.create_goal(db, payload)


@router.get("/goals", response_model=list[Goal])
def list_goals(status: str | None = None, db: Session = Depends(get_db)):
    return workout_service.list_goals(db, status=status)


@router.patch("/goals/{goal_id}", response_model=Goal)
def update_goal(goal_id: int, payload: GoalUpdate, db: Session = Depends(get_db)):
    goal = workout_service.update_goal(db, goal_id, payload)
    if goal is None:
        raise HTTPException(status_code=404, detail="Goal not found")
    return goal
