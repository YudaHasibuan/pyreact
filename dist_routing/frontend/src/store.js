import { useState, useEffect } from "react";

const listeners = new Set();
let globalState = {
  current_user: null,
  is_loading: false,
};

export const setSharedState = (nextState) => {
  globalState = typeof nextState === "function" ? nextState(globalState) : { ...globalState, ...nextState };
  for (const listener of listeners) {
    listener(globalState);
  }
};

export const getSharedState = () => globalState;

export const useSharedState = () => {
  const [state, setState] = useState(globalState);
  useEffect(() => {
    listeners.add(setState);
    return () => { listeners.delete(setState); };
  }, []);
  return [state, setSharedState];
};
