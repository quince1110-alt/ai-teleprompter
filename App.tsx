import React, { useState, useRef } from 'react';
import { AppState } from './types';
import { analyzeAudio } from './services/geminiService';
import AudioVisualizer from './components/AudioVisualizer';
import ResultDisplay from './components/ResultDisplay';

// Icons
const MicIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="22"/></svg>
);
const SquareIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="6" y="6" width="12" height="12" /></svg>
);
const RefreshIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"/><path d="M16 21h5v-5"/></svg>
);

// Logo Component (Recreated based on provided image: Abstract white lines on black squircle)
const AppLogo = () => (
  <div className="w-24 h-24 bg-black rounded-[2.5rem] flex items-center justify-center mb-8 shadow-2xl ring-4 ring-black/5">
    <svg width="56" height="56" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
        {/* Abstract Geometry imitating the provided logo */}
        <path d="M12 24 L32 40 L52 24" stroke="white" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M22 24 L32 32 L42 24" stroke="white" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
        
        {/* Radiating / Floating lines */}
        <path d="M16 46 L10 52" stroke="white" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M48 46 L54 52" stroke="white" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
        
        {/* Center details */}
        <path d="M32 16 L32 20" stroke="white" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
        <circle cx="26" cy="42" r="2" fill="white"/>
        <circle cx="32" cy="46" r="2" fill="white"/>
        <circle cx="38" cy="42" r="2" fill="white"/>
    </svg>
  </div>
);

const App: React.FC = () => {
  const [appState, setAppState] = useState<AppState>(AppState.IDLE);
  const [analysisResult, setAnalysisResult] = useState<string>('');
  const [errorMsg, setErrorMsg] = useState<string>('');
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const [mediaStream, setMediaStream] = useState<MediaStream | null>(null);

  const startRecording = async () => {
    setErrorMsg('');
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      setMediaStream(stream);
      
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      mediaRecorder.onstop = handleRecordingStop;
      mediaRecorder.start();
      setAppState(AppState.RECORDING);
    } catch (err) {
      console.error(err);
      setErrorMsg("请允许麦克风权限以使用导演功能。");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
      if (mediaStream) {
        mediaStream.getTracks().forEach(track => track.stop());
        setMediaStream(null);
      }
    }
  };

  const handleRecordingStop = async () => {
    setAppState(AppState.PROCESSING);
    const blob = new Blob(chunksRef.current, { type: 'audio/webm' }); 
    
    try {
      const result = await analyzeAudio(blob);
      setAnalysisResult(result);
      setAppState(AppState.RESULT);
    } catch (err: any) {
        if(err.message.includes("API Key")) {
             setErrorMsg("API Key 缺失。请在环境中配置。");
        } else {
            setErrorMsg("导演没听清，请再试一次。");
        }
      setAppState(AppState.ERROR);
    }
  };

  const resetApp = () => {
    setAppState(AppState.IDLE);
    setAnalysisResult('');
    setErrorMsg('');
  };

  return (
    <div className="min-h-screen bg-[#F2F0E9] text-[#1a1a1a] flex flex-col items-center py-16 px-6 font-serif selection:bg-black selection:text-white">
      
      {/* Header */}
      <header className="mb-16 flex flex-col items-center text-center space-y-4">
        <AppLogo />
        <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-black">
          AI 视频导演
        </h1>
        <p className="text-[#5c5c5c] text-sm md:text-base max-w-md font-sans">
          捕捉瞬间的灵感，即刻生成专业的拍摄脚本。
        </p>
      </header>

      {/* Main Interaction Area */}
      <main className="w-full max-w-3xl flex flex-col items-center gap-10">
        
        {/* Error Message */}
        {errorMsg && (
          <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded text-sm">
            {errorMsg}
          </div>
        )}

        {/* State: IDLE or ERROR */}
        {(appState === AppState.IDLE || appState === AppState.ERROR) && (
          <div className="flex flex-col items-center gap-8 animate-fade-in">
            <button 
              onClick={startRecording}
              className="group relative bg-black hover:bg-[#333] text-[#F2F0E9] w-36 h-36 rounded-full flex flex-col items-center justify-center transition-all transform hover:scale-105 active:scale-95 shadow-2xl"
            >
               <div className="absolute inset-0 border border-white/20 rounded-full scale-90 group-hover:scale-100 transition-transform duration-500"></div>
              <MicIcon />
              <span className="mt-3 text-xs font-sans tracking-widest opacity-80 group-hover:opacity-100">点击录音</span>
            </button>
            <p className="text-[#8a8a8a] text-xs font-sans tracking-wide uppercase">点击开始</p>
          </div>
        )}

        {/* State: RECORDING */}
        {appState === AppState.RECORDING && (
          <div className="flex flex-col items-center gap-8 w-full animate-fade-in">
            <div className="text-red-600 font-bold font-sans text-xs tracking-widest animate-pulse flex items-center gap-2">
              <span className="w-2 h-2 bg-red-600 rounded-full"></span>
              录音中...
            </div>
            
            <AudioVisualizer isRecording={true} mediaStream={mediaStream} />

            <button 
              onClick={stopRecording}
              className="bg-black hover:bg-[#333] text-white w-20 h-20 rounded-full flex items-center justify-center shadow-lg transition-all transform hover:scale-110 active:scale-95"
            >
              <SquareIcon />
            </button>
             <p className="text-[#8a8a8a] text-xs font-sans">点击完成</p>
          </div>
        )}

        {/* State: PROCESSING */}
        {appState === AppState.PROCESSING && (
          <div className="flex flex-col items-center gap-8 animate-fade-in py-10">
            <div className="w-16 h-16 border-4 border-[#d4d1c9] border-t-black rounded-full animate-spin"></div>
            <div className="text-center space-y-2">
              <h3 className="text-xl font-bold text-black">正在分析语感与逻辑...</h3>
              <p className="text-[#666] text-sm font-sans">导演正在为您撰写脚本</p>
            </div>
          </div>
        )}

        {/* State: RESULT */}
        {appState === AppState.RESULT && (
          <div className="w-full animate-fade-in-up">
            <div className="flex justify-between items-end mb-8 border-b-2 border-black pb-4">
              <h2 className="text-2xl font-bold text-black">
                拍摄方案
              </h2>
              <button 
                onClick={resetApp}
                className="flex items-center gap-2 text-sm text-[#666] hover:text-black transition-colors font-sans"
              >
                <RefreshIcon />
                重新开始
              </button>
            </div>
            
            <ResultDisplay content={analysisResult} />
            
            <div className="mt-16 text-center">
                 <button 
                onClick={resetApp}
                className="px-10 py-4 bg-black hover:bg-[#333] text-[#F2F0E9] rounded-full font-bold text-sm tracking-wider transition-all shadow-lg hover:shadow-xl font-sans"
              >
                录制下一条
              </button>
            </div>
          </div>
        )}

      </main>

      {/* Footer */}
      <footer className="fixed bottom-6 text-[#999] text-[10px] font-sans tracking-widest uppercase">
        AI Video Director • Gemini 2.5
      </footer>
    </div>
  );
};

export default App;