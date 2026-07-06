import { create } from "zustand";

type AppState = {
  activeModule: string;
  isDarkMode: boolean;
  setActiveModule: (module: string) => void;
  toggleDarkMode: () => void;
};

export const useAppStore = create<AppState>((set) => ({
  activeModule: "dashboard",
  isDarkMode: false,
  setActiveModule: (activeModule) => set({ activeModule }),
  toggleDarkMode: () => set((state) => ({ isDarkMode: !state.isDarkMode })),
}));
