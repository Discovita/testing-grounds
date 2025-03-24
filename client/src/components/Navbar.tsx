import { ThemeSwitcher } from "@/components/ThemeSwitcher";
import { Link } from "react-router-dom";

/**
 * Navbar Component
 *
 * Main navigation component that provides access to different sections of the application
 * and includes the theme switcher functionality.
 */
export default function Navbar() {
  return (
    <div className="_Navbar flex items-center justify-between px-4 py-2 bg-background border-b">
      <div className="flex items-center gap-6">
        <Link to="/" className="text-lg font-semibold">
          Home
        </Link>
        <Link
          to="/renovation-journey"
          className="text-lg hover:text-primary transition-colors"
        >
          Renovation Journey
        </Link>
        <Link
          to="/admin"
          className="text-lg hover:text-primary transition-colors"
        >
          Admin Dashboard
        </Link>
      </div>
      <ThemeSwitcher />
    </div>
  );
}
