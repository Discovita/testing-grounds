import { Routes, Route } from "react-router-dom";
import Layout from "@/layout/Layout";
import Home from "@/pages/Home";
import RenovationJourney from "@/pages/RenovationJourney";
import AdminDashboard from "@/pages/AdminDashboard";


/**
 * Main App component
 * Defines the routing structure for the entire application
 * Each route is associated with a specific tool or feature
 */
const App = () => {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Home />} />
        <Route path="/renovation-journey" element={<RenovationJourney />} />
        <Route path="/admin" element={<AdminDashboard />} />
      </Route>
    </Routes>
  );
};

export default App;
