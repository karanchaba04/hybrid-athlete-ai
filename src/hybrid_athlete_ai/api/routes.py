from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from hybrid_athlete_ai.database import get_db
from hybrid_athlete_ai.models.enums import RxStatus
from hybrid_athlete_ai.models.goal import Goal, GoalCreate, GoalUpdate
from hybrid_athlete_ai.schemas.quick import QuickWorkoutCreate
from hybrid_athlete_ai.schemas.training import (
    CrossFitHistorySummary,
    PersonalRecord,
    RepRecord,
    RepRecordSummary,
    RunningHistoryEntry,
    TrainingSessionCreate,
    TrainingSessionRead,
    WeeklyVolume,
    WorkoutDefinitionRead,
)
from hybrid_athlete_ai.services import workout_service
from hybrid_athlete_ai.services.crossfit_analytics import get_crossfit_history, list_workout_definitions
from hybrid_athlete_ai.services.rep_records import (
    get_lift_rep_summary,
    get_movement_history,
    get_strength_rep_summary,
    list_lift_movements,
)
from hybrid_athlete_ai.services.running_analytics import get_running_history
from hybrid_athlete_ai.services.strength_history import StrengthHistoryEntry, get_strength_history


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


@router.get("/analytics/rep-records", response_model=RepRecordSummary)
def get_rep_records(
    movement: str,
    source: str = Query(default="strength", pattern="^(strength|olympic)$"),
    db: Session = Depends(get_db),
):
    if source == "olympic":
        return get_lift_rep_summary(db, movement)
    return get_strength_rep_summary(db, movement)


@router.get("/analytics/movement-history", response_model=list[RepRecord])
def get_movement_history_endpoint(
    movement: str,
    db: Session = Depends(get_db),
):
    return get_movement_history(db, movement)


@router.get("/analytics/barbell-logbook", response_model=list[RepRecordSummary])
def get_barbell_logbook(db: Session = Depends(get_db)):
    movements = list_lift_movements(db)
    return [get_lift_rep_summary(db, movement) for movement in movements]


@router.get("/analytics/running-history", response_model=list[RunningHistoryEntry])
def get_running_history_endpoint(
    weeks: int = Query(default=12, ge=1, le=52),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    return get_running_history(db, weeks=weeks, limit=limit)


@router.get("/analytics/crossfit/workouts", response_model=list[WorkoutDefinitionRead])
def get_crossfit_workouts(db: Session = Depends(get_db)):
    return list_workout_definitions(db)


@router.get("/analytics/crossfit/history", response_model=CrossFitHistorySummary)
def get_crossfit_history_endpoint(
    workout_name: str | None = None,
    workout_id: int | None = None,
    rx_status: RxStatus | None = None,
    db: Session = Depends(get_db),
):
    summary = get_crossfit_history(
        db,
        workout_name=workout_name,
        workout_id=workout_id,
        rx_status=rx_status,
    )
    if summary is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    return summary


@router.get("/analytics/weekly-volume", response_model=WeeklyVolume)
def get_weekly_volume(
    reference_date: date | None = None,
    db: Session = Depends(get_db),
):
    return workout_service.get_weekly_volume(db, reference_date=reference_date)


@router.get("/analytics/strength-history", response_model=list[StrengthHistoryEntry])
def get_strength_history_endpoint(
    exercise_name: str,
    weeks: int = Query(default=12, ge=1, le=52),
    db: Session = Depends(get_db),
):
    return get_strength_history(db, exercise_name=exercise_name, weeks=weeks)


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
