/**
 * RenovationJourney.tsx
 *
 * This is the main page for the renovation journey application.
 * It integrates the various components to create a complete user experience.
 * The page manages the overall state of the journey and coordinates between components.
 */

import { useState, useEffect } from "react";
import { SessionStartForm } from "@/components/SessionStartForm";
import { Conversation } from "@/components/Conversation";
import { JourneyProgress } from "@/components/JourneyProgress";
import {
  useGetActiveJourney,
  useCompleteJourney,
  JourneyStateResponse,
  useGetJourney
} from "@/api";

// Constants for localStorage keys
const STORAGE_USER_ID = "renovation_user_id";
const STORAGE_JOURNEY_ID = "renovation_journey_id";

/**
 * RenovationJourney is the main page component for the renovation journey application.
 * It handles the user session and renders different UI based on the current state.
 * The state is persisted in localStorage to allow users to continue where they left off.
 */
export default function RenovationJourney() {
  // State for tracking the current user and journey
  const [userId, setUserId] = useState<number | null>(null);
  const [journeyId, setJourneyId] = useState<number | null>(null);

  // State for real-time journey updates from the Conversation component
  const [journeyState, setJourneyState] = useState<JourneyStateResponse | null>(
    null
  );

  // Load saved session on initial render
  useEffect(() => {
    const savedUserId = localStorage.getItem(STORAGE_USER_ID);
    const savedJourneyId = localStorage.getItem(STORAGE_JOURNEY_ID);

    if (savedUserId && savedJourneyId) {
      setUserId(parseInt(savedUserId, 10));
      setJourneyId(parseInt(savedJourneyId, 10));
    }
  }, []);

  // Fetch the active journey if we have a user ID
  const {
    data: journey,
    isLoading,
    isError,
    error
  } = useGetActiveJourney(userId || 0, {
    // Skip the query if we don't have a user ID yet
    enabled: !!userId,
    // The options object is not a full UseQueryOptions - it's filtered by the hook
    // so we don't need to specify queryKey
  });

  // Add specific query to get a journey by ID (needed for completion)
  const {
    data: completedJourneyData,
    isLoading: isCompletedJourneyLoading,
    refetch: refetchCompletedJourney
  } = useGetJourney(journeyId || 0, {
    enabled: false, // Don't run automatically, we'll trigger it manually
  });

  // Mutations for milestone advancement and journey completion
  const { mutate: completeJourney } = useCompleteJourney();

  // Check if the journey is completed from either API or real-time updates
  const isJourneyCompleted =
    (journey && journey.status === "completed") ||
    (journeyState && journeyState.status === "completed") ||
    (completedJourneyData && completedJourneyData.status === "completed");

  // Ensure we fetch the most up-to-date data for completed journeys
  useEffect(() => {
    if (isJourneyCompleted && journeyId && !completedJourneyData) {
      // If journey is completed but we don't have the completed journey data, fetch it
      refetchCompletedJourney();
    }
  }, [isJourneyCompleted, journeyId, completedJourneyData, refetchCompletedJourney]);

  // Handler for when a session is started
  const handleSessionStarted = ({
    userId,
    journeyId,
  }: {
    userId: number;
    journeyId: number;
  }) => {
    // Save session data to localStorage for persistence
    localStorage.setItem(STORAGE_USER_ID, userId.toString());
    localStorage.setItem(STORAGE_JOURNEY_ID, journeyId.toString());

    setUserId(userId);
    setJourneyId(journeyId);
  };

  // Handler for completing the journey
  const handleCompleteJourney = () => {
    if (journeyId) {
      completeJourney(journeyId);
    }
  };

  // Handler for journey state updates from the Conversation component
  const handleJourneyStateUpdate = (newState: JourneyStateResponse) => {
    setJourneyState(newState);

    // Log detailed updates in development mode
    if (process.env.NODE_ENV === "development") {
      console.group("Journey State Update");
      console.log("Milestone:", newState.milestone);
      console.log("Status:", newState.status);
      console.log("Completed checkpoints:", newState.completed_checkpoints);
      console.groupEnd();
    }

    // If journey is completed, we should clean up localStorage in handleCompleteJourney
    // and refetch the journey to get the latest data
    if (newState.status === "completed") {
      handleCompleteJourney();
      
      // Refetch the journey to get the latest data including all checkpoints
      refetchCompletedJourney().then(() => {
        console.log("Refetched completed journey data");
      });
    }
  };

  // Handler for starting a new journey (clears localStorage)
  const handleStartNewJourney = () => {
    localStorage.removeItem(STORAGE_USER_ID);
    localStorage.removeItem(STORAGE_JOURNEY_ID);

    setUserId(null);
    setJourneyId(null);
    setJourneyState(null);
  };

  // If we don't have a user ID yet, show the session start form
  if (!userId || !journeyId) {
    return (
      <div className="min-h-screen bg-gray-100 dark:bg-slate-900 flex flex-col justify-center w-full">
        <div className="py-12">
          <SessionStartForm onSessionStarted={handleSessionStarted} />
        </div>
      </div>
    );
  }

  // Loading state
  if (isLoading && !journeyState) {
    return (
      <div className="min-h-screen bg-gray-100 dark:bg-slate-900 flex items-center justify-center w-full">
        <p className="text-xl text-gray-500">Loading your journey...</p>
      </div>
    );
  }

  // Error state
  if (isError && !journeyState) {
    return (
      <div className="min-h-screen bg-gray-100 dark:bg-slate-900 flex items-center justify-center w-full">
        <div className="bg-white dark:bg-slate-800 rounded-lg shadow-md p-6 max-w-md w-full">
          <h2 className="text-xl font-bold text-red-500 mb-4">Error</h2>
          <p className="text-gray-700 dark:text-gray-300 mb-4">
            {error.message || "Failed to load your journey."}
          </p>
          <button
            onClick={handleStartNewJourney}
            className="bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded-md"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  // Use the latest journey state (either from API or real-time updates)
  const currentJourneyState =
    journeyState ||
    (journey
      ? ({
          milestone: journey.current_milestone,
          completed_checkpoints: [
            ...(journey.room ? ["room"] : []),
            ...(journey.renovation_purpose ? ["renovation_purpose"] : []),
            ...(journey.budget_range ? ["budget_range"] : []),
            ...(journey.timeline ? ["timeline"] : []),
            ...(journey.style_preference ? ["style_preference"] : []),
            ...(journey.priority_feature ? ["priority_feature"] : []),
          ],
          status: journey.status,
        } as JourneyStateResponse)
      : null);

  // Journey completed state
  if (isJourneyCompleted) {
    // If we have completed journey data from our specific query, use that
    // Otherwise fall back to journey or journeyState
    const journeyData = completedJourneyData || journey;
    
    // Get journey data from the most up-to-date source with complete details
    const journeyDetails = {
      room: journeyData?.room || "",
      renovation_purpose: journeyData?.renovation_purpose || "",
      budget_range: journeyData?.budget_range || "",
      timeline: journeyData?.timeline || "",
      style_preference: journeyData?.style_preference || "",
      priority_feature: journeyData?.priority_feature || ""
    };
    
    // Log journey details for debugging
    if (process.env.NODE_ENV === "development") {
      console.group("Completed Journey Details");
      console.log("Completed Journey from API:", completedJourneyData);
      console.log("Original Journey:", journey);
      console.log("Journey State:", journeyState);
      console.log("Final Journey Details:", journeyDetails);
      console.groupEnd();
    }
    
    // Show loading state while fetching completed journey data
    if (isCompletedJourneyLoading) {
      return (
        <div className="min-h-screen bg-gray-100 dark:bg-slate-900 flex items-center justify-center">
          <p className="text-xl text-gray-500">Loading your completed journey...</p>
        </div>
      );
    }
    
    return (
      <div className="min-h-screen bg-gray-100 dark:bg-slate-900 flex items-center justify-center w-full">
        <div className="bg-white dark:bg-slate-800 rounded-lg shadow-md p-6 max-w-md w-full">
          <h2 className="text-2xl font-bold text-gray-800 dark:text-white mb-4">
            Your Journey is Complete!
          </h2>
          <p className="text-gray-700 dark:text-gray-300 mb-6">
            Thank you for planning your renovation with us. Here's a summary of
            your journey:
          </p>
          <div className="space-y-3 mb-6">
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Room:</span>
              <span className="font-medium text-gray-800 dark:text-white">
                {journeyDetails.room}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Purpose:</span>
              <span className="font-medium text-gray-800 dark:text-white">
                {journeyDetails.renovation_purpose}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Budget:</span>
              <span className="font-medium text-gray-800 dark:text-white">
                {journeyDetails.budget_range}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">
                Timeline:
              </span>
              <span className="font-medium text-gray-800 dark:text-white">
                {journeyDetails.timeline}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Style:</span>
              <span className="font-medium text-gray-800 dark:text-white">
                {journeyDetails.style_preference || "N/A"}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">
                Priority:
              </span>
              <span className="font-medium text-gray-800 dark:text-white">
                {journeyDetails.priority_feature || "N/A"}
              </span>
            </div>
          </div>
          <button
            onClick={handleStartNewJourney}
            className="w-full bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded-md"
          >
            Start a New Journey
          </button>
        </div>
      </div>
    );
  }

  // Main journey UI
  return (
    <div className="min-h-screen bg-gray-100 dark:bg-slate-900 w-full">
      <div className="container mx-auto py-8 px-4 md:px-6">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800 dark:text-white">
            Renovation Planning Journey
          </h1>
          <button
            onClick={handleStartNewJourney}
            className="bg-red-500 hover:bg-red-600 text-white py-2 px-4 rounded-md text-sm"
          >
            Sign Out
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Journey progress sidebar */}
          <div className="lg:col-span-1">
            <JourneyProgress
              userId={userId}
              journeyState={currentJourneyState || undefined}
            />
          </div>

          {/* Chat area */}
          <div className="lg:col-span-2">
            <div className="bg-white dark:bg-slate-800 rounded-lg shadow-md overflow-hidden h-[600px]">
              <Conversation
                userId={userId}
                journeyId={journeyId}
                onJourneyStateUpdate={handleJourneyStateUpdate}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
