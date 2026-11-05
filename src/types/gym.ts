export type Language = 'en' | 'vi';

export interface ExerciseSteps {
  prepare: string[];
  execution: string[];
  breathing: string[];
}

export interface Exercise {
  id: string;
  slug: string;
  name: string;
  nameVi?: string;
  aliases: string[];
  category: string;
  equipment: string;
  videoUrl: string;
  primaryMuscles: string[];
  secondaryMuscles: string[];
  primarySlugs: string[];
  secondarySlugs: string[];
  shortDescription: string;
  steps: ExerciseSteps;
  stepsVi?: ExerciseSteps;
}

export interface WorkoutSet {
  weight: number;
  reps: number;
  type?: 'normal' | 'warmup' | 'drop';
}

export interface RoutineExerciseItem {
  exerciseId: string;
  sets: WorkoutSet[];
  note?: string;
  isWarmup?: boolean;
}

export interface Routine {
  id: string;
  name: string;
  tag: string;
  exercises: RoutineExerciseItem[];
}

export type ActiveTab = 'routines' | 'wiki' | 'backup';

export type ScreenRoute =
  | { name: 'routineList' }
  | { name: 'routineDetail'; routineId: string }
  | { name: 'wikiList' }
  | {
      name: 'exerciseInfo';
      exerciseId: string;
      routineId?: string;
      routineExIndex?: number;
      returnTo: ScreenRoute;
    }
  | { name: 'backup' };
