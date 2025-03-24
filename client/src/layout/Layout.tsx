import Navbar from "@/components/Navbar";
import { Outlet } from "react-router-dom";

const Layout = () => {
  return (
    <div className="_Layout flex h-screen w-full flex-col overflow-clip">
      <nav className="relative z-[1000] flex-none">
        <Navbar />
      </nav>
      <main className="_Main flex justify-center overflow-clip">
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;
