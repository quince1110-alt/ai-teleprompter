export enum AppState {
  IDLE = 'IDLE',
  RECORDING = 'RECORDING',
  PROCESSING = 'PROCESSING',
  RESULT = 'RESULT',
  ERROR = 'ERROR'
}

export interface DirectorResponse {
  markdown: string;
}

export interface AudioVisualizerProps {
  isRecording: boolean;
  mediaStream: MediaStream | null;
}
