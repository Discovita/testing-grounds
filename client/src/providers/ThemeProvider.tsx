import { useEffect, useState, ReactNode } from "react";
import { ThemeContext } from "@/context/ThemeContext";

export function ThemeProvider({
  children,
  defaultTheme = "light",
  storageKey = "vite-ui-theme",
  ...props
}: {
  children: ReactNode;
  defaultTheme?: string;
  storageKey?: string;
}) {
  const [theme, setTheme] = useState(() => {
    const savedTheme = localStorage.getItem(storageKey);
    return savedTheme || defaultTheme;
  });

  useEffect(() => {
    const root = window.document.documentElement;

    if (theme === "system") {
      // Remove any explicit theme class
      root.classList.remove("dark");
      localStorage.removeItem(storageKey);
      return;
    }

    // For explicit theme choices
    if (theme === "dark") {
      root.classList.add("dark");
    } else {
      root.classList.remove("dark");
    }
  }, [theme, storageKey]);

  const value = {
    theme,
    setTheme: (theme: string) => {
      localStorage.setItem(storageKey, theme);
      setTheme(theme);
    },
  };

  return (
    <ThemeContext.Provider {...props} value={value}>
      {children}
    </ThemeContext.Provider>
  );
}
