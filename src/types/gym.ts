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
  supersetId?: string;
  restSeconds?: number;
}

export interface Routine {
  id: string;
  name: string;
  tag: string;
  exercises: RoutineExerciseItem[];
}

export type ActiveTab = 'routines' | 'wiki';

export type ScreenRoute =
  | { name: 'routineList' }
  | {
      name: 'routineDetail';
      routineId: string;
      initialEditMode?: boolean;
      scrollToIndex?: number;
      savedScrollY?: number;
    }
  | { name: 'wikiList'; savedScrollY?: number }
  | {
      name: 'exercisePicker';
      routineId: string;
      asWarmup: boolean;
      replacingExIdx: number | null;
      searchQuery?: string;
      muscleFilter?: string;
      equipmentFilter?: string;
      fromEditMode?: boolean;
    }
  | {
      name: 'exerciseInfo';
      exerciseId: string;
      routineId?: string;
      routineExIndex?: number;
      asWarmup?: boolean;
      replacingExIdx?: number | null;
      returnTo: ScreenRoute;
    };
