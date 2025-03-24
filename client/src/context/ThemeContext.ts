import { createContext, useContext } from "react";

interface ThemeContextType {
  theme: string;
  setTheme: (theme: string) => void;
}

// Remove the initialState object - we'll make the context null initially
export const ThemeContext = createContext<ThemeContextType | null>(null);

// Add a custom hook to ensure type safety and proper error handling
export function useThemeContext() {
  const context = useContext(ThemeContext);
  if (context === null) {
    throw new Error("useThemeContext must be used within a ThemeProvider");
  }
  return context;
}
