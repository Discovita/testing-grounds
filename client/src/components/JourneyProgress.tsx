/**
 * JourneyProgress.tsx
 *
 * This component displays the current progress of a user's renovation journey.
 * It shows the current milestone and checkpoints that have been completed.
 * It uses React Query to fetch the journey state from the API.
 */

import { useEffect } from "react";
import { useGetJourneyState } from "@/api";
import { JourneyStateResponse } from "@/api/models";

/**
 * JourneyProgressProps
 * @property {number} userId - The ID of the current user
 */
interface JourneyProgressProps {
  userId: number;
  journeyState?: JourneyStateResponse; // Optional direct state prop for real-time updates
}

/**
 * Icons for different milestone states
 */
const MilestoneIcons = {
  completed: (
    <svg
      className="w-6 h-6 text-green-500"
      fill="currentColor"
      viewBox="0 0 20 20"
    >
      <path
        fillRule="evenodd"
        d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
        clipRule="evenodd"
      />
    </svg>
  ),
  current: (
    <svg
      className="w-6 h-6 text-blue-500"
      fill="currentColor"
      viewBox="0 0 20 20"
    >
      <path
        fillRule="evenodd"
        d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
        clipRule="evenodd"
      />
    </svg>
  ),
  upcoming: (
    <svg
      className="w-6 h-6 text-gray-300"
      fill="currentColor"
      viewBox="0 0 20 20"
    >
      <path
        fillRule="evenodd"
        d="M10 18a8 8 0 100-16 8 8 0 000 16zm0-2a6 6 0 100-12 6 6 0 000 12z"
        clipRule="evenodd"
      />
    </svg>
  ),
};

/**
 * MilestoneCheckpoints maps each milestone to its checkpoints
 */
const MilestoneCheckpoints = {
  1: ["room", "renovation_purpose"],
  2: ["budget_range", "timeline"],
  3: ["style_preference", "priority_feature"],
};

/**
 * Human-readable names for each checkpoint
 */
const CheckpointLabels: Record<string, string> = {
  room: "Room to Renovate",
  renovation_purpose: "Renovation Purpose",
  budget_range: "Budget Range",
  timeline: "Timeline",
  style_preference: "Style Preference",
  priority_feature: "Priority Feature",
};

/**
 * Human-readable names for each milestone
 */
const MilestoneNames = [
  "Project Basics",
  "Budget and Timeline",
  "Style Preferences and Plan",
];

/**
 * JourneyProgress component displays the user's progress through the renovation journey.
 * It shows all milestones and the checkpoints completed throughout the journey.
 *
 * @param userId - ID of the current user
 * @param journeyState - Optional direct journey state for real-time updates
 */
export function JourneyProgress({
  userId,
  journeyState: providedState,
}: JourneyProgressProps) {
  // Fetch the current journey state if not provided directly
  const {
    data: fetchedState,
    isLoading,
    isError,
    error,
    refetch,
  } = useGetJourneyState(userId, {
    enabled: !providedState, // Only fetch if state not provided
  });

  // Refresh journey state when component mounts or userId changes
  useEffect(() => {
    if (!providedState) {
      refetch();

      // Set up periodic refreshing every 30 seconds
      const intervalId = setInterval(() => {
        refetch();
      }, 30000);

      // Clean up interval on unmount
      return () => clearInterval(intervalId);
    }
  }, [userId, providedState, refetch]);

  // Use provided state if available, otherwise use fetched state
  const state = providedState || fetchedState;

  if (isLoading && !providedState) {
    return (
      <div className="text-center p-4">
        <p className="text-gray-500">Loading journey progress...</p>
      </div>
    );
  }

  if (isError && !providedState) {
    return (
      <div className="text-red-500 text-center p-4">
        <p>Error: {error.message || "Failed to load journey state"}</p>
        <button
          onClick={() => refetch()}
          className="mt-2 bg-blue-500 hover:bg-blue-600 text-white py-1 px-3 rounded-md text-sm"
        >
          Try Again
        </button>
      </div>
    );
  }

  if (!state) {
    return (
      <div className="text-center p-4">
        <p className="text-gray-500">No active journey found.</p>
      </div>
    );
  }

  const { milestone, completed_checkpoints, status } = state;

  // Helper functions
  const isMilestoneCompleted = (milestoneNum: number) => {
    // If we've advanced beyond this milestone, it must be complete
    if (milestoneNum < milestone) {
      return true;
    }
    // Otherwise check if all its checkpoints are completed
    const currentCheckpoints =
      MilestoneCheckpoints[milestoneNum as keyof typeof MilestoneCheckpoints] ||
      [];
    return currentCheckpoints.every((cp) => completed_checkpoints.includes(cp));
  };

  // Check if a specific checkpoint is completed
  const isCheckpointCompleted = (checkpoint: string, milestoneNum: number) => {
    // If we've advanced beyond this milestone, all its checkpoints must be complete
    if (milestoneNum < milestone) {
      return true;
    }
    // Otherwise check if this checkpoint is in the completed list
    return completed_checkpoints.includes(checkpoint);
  };

  // Get milestone status (completed, current, upcoming)
  const getMilestoneStatus = (milestoneNum: number) => {
    if (milestoneNum < milestone) return "completed";
    if (milestoneNum === milestone) return "current";
    return "upcoming";
  };

  // Get percentage of journey completed
  const getCompletionPercentage = () => {
    let completedCount = 0;
    
    // Count all checkpoints in completed milestones
    for (let i = 1; i < milestone; i++) {
      const milestoneCPs = MilestoneCheckpoints[i as keyof typeof MilestoneCheckpoints] || [];
      completedCount += milestoneCPs.length;
    }
    
    // Add checkpoints from current milestone
    if (milestone <= 3) {
      const currentMilestoneCPs = MilestoneCheckpoints[milestone as keyof typeof MilestoneCheckpoints] || [];
      completedCount += currentMilestoneCPs.filter(cp => completed_checkpoints.includes(cp)).length;
    }
    
    const totalCheckpoints = 6; // 2 per milestone
    return Math.round((completedCount / totalCheckpoints) * 100);
  };

  // Calculate milestone completion percentages for the segmented progress bar
  const getMilestoneCompletionData = () => {
    const milestonesData = [1, 2, 3].map((milestoneNum) => {
      const checkpoints =
        MilestoneCheckpoints[milestoneNum as keyof typeof MilestoneCheckpoints];
      
      // If we've moved past this milestone, it's 100% complete
      if (milestoneNum < milestone) {
        return {
          milestoneNum,
          completedCount: checkpoints.length,
          totalCount: checkpoints.length,
          percentage: 100
        };
      }
      
      // Otherwise count completed checkpoints
      const completedCount = checkpoints.filter((cp) =>
        completed_checkpoints.includes(cp)
      ).length;
      const totalCount = checkpoints.length;
      const percentage = (completedCount / totalCount) * 100;

      return {
        milestoneNum,
        completedCount,
        totalCount,
        percentage,
      };
    });

    return milestonesData;
  };

  // Get milestone color based on completion status
  const getMilestoneColor = (milestoneNum: number) => {
    const status = getMilestoneStatus(milestoneNum);
    if (status === "completed") return "bg-green-500";
    if (status === "current") {
      // For current milestone, check partial completion
      const checkpoints =
        MilestoneCheckpoints[milestoneNum as keyof typeof MilestoneCheckpoints];
      const completedCount = checkpoints.filter((cp) =>
        completed_checkpoints.includes(cp)
      ).length;
      if (completedCount > 0) return "bg-blue-500";
      return "bg-blue-300";
    }
    return "bg-gray-300";
  };

  // Milestone completion data for segmented progress bar
  const milestoneCompletionData = getMilestoneCompletionData();

  return (
    <div className="bg-white dark:bg-slate-800 rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-gray-800 dark:text-white">
          Your Journey
        </h2>
        <div
          className={`px-3 py-1 rounded-full text-sm font-medium
          ${
            status === "completed"
              ? "bg-green-100 text-green-800"
              : status === "abandoned"
              ? "bg-red-100 text-red-800"
              : "bg-blue-100 text-blue-800"
          }`}
        >
          {status === "in_progress" ? "In Progress" : status}
        </div>
      </div>

      {/* Progress bar */}
      <div className="relative pt-1 mb-6">
        <div className="flex items-center justify-between mb-1">
          <div>
            <span className="text-xs font-semibold inline-block text-blue-600">
              Progress
            </span>
          </div>
          <div className="text-right">
            <span className="text-xs font-semibold inline-block text-blue-600">
              {getCompletionPercentage()}%
            </span>
          </div>
        </div>

        {/* Segmented progress bar */}
        <div className="overflow-hidden h-2 mb-1 text-xs flex rounded bg-gray-200 dark:bg-gray-700">
          {/* Show each milestone as a segment */}
          {milestoneCompletionData.map((milestone, index) => {
            // Calculate segment percentage (each milestone is 1/3 of total width)
            const segmentWidth = 33.33;

            return (
              <div
                key={milestone.milestoneNum}
                className="relative"
                style={{ width: `${segmentWidth}%` }}
              >
                {milestone.completedCount > 0 && (
                  <div
                    className={`absolute top-0 left-0 h-full transition-all duration-500 ${getMilestoneColor(
                      milestone.milestoneNum
                    )}`}
                    style={{ width: `${milestone.percentage}%` }}
                  />
                )}
                {/* Milestone dividers */}
                {index < 2 && (
                  <div className="absolute right-0 top-0 h-full w-0.5 bg-white dark:bg-gray-800 z-10"></div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      <div className="space-y-6">
        {/* Milestone timeline */}
        <div className="flex items-center justify-between">
          {[1, 2, 3].map((milestoneNum) => {
            const status = getMilestoneStatus(milestoneNum);

            return (
              <div key={milestoneNum} className="flex flex-col items-center">
                <div className="mb-2">
                  {MilestoneIcons[status as keyof typeof MilestoneIcons]}
                </div>
                <div className="text-sm font-medium text-gray-800 dark:text-white">
                  Milestone {milestoneNum}
                </div>
              </div>
            );
          })}
        </div>

        {/* All milestone details */}
        <div className="space-y-6">
          {[1, 2, 3].map((milestoneNum) => {
            const milestoneStatus = getMilestoneStatus(milestoneNum);
            const isCompletedMilestone = isMilestoneCompleted(milestoneNum);
            const isActiveMilestone = milestoneNum === milestone;

            return (
              <div
                key={milestoneNum}
                className={`border rounded-lg p-4 ${
                  isActiveMilestone
                    ? "border-blue-300 bg-blue-50 dark:bg-slate-700 dark:border-blue-700"
                    : "border-gray-200 dark:border-gray-700"
                }`}
              >
                <h3
                  className={`font-medium mb-2 flex items-center ${
                    isActiveMilestone
                      ? "text-blue-700 dark:text-blue-400"
                      : "text-gray-800 dark:text-gray-200"
                  }`}
                >
                  {milestoneStatus === "completed" && (
                    <svg
                      className="w-4 h-4 text-green-500 mr-2"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fillRule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                        clipRule="evenodd"
                      />
                    </svg>
                  )}
                  {isActiveMilestone && (
                    <svg
                      className="w-4 h-4 text-blue-500 mr-2"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fillRule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                        clipRule="evenodd"
                      />
                    </svg>
                  )}
                  Milestone {milestoneNum}: {MilestoneNames[milestoneNum - 1]}
                </h3>

                <div className="space-y-2">
                  {MilestoneCheckpoints[
                    milestoneNum as keyof typeof MilestoneCheckpoints
                  ].map((checkpoint) => {
                    const isCheckpointDone = isCheckpointCompleted(checkpoint, milestoneNum);

                    return (
                      <div key={checkpoint} className="flex items-center">
                        <div className="mr-2">
                          {isCheckpointDone ? (
                            <svg
                              className="w-4 h-4 text-green-500"
                              fill="currentColor"
                              viewBox="0 0 20 20"
                            >
                              <path
                                fillRule="evenodd"
                                d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                                clipRule="evenodd"
                              />
                            </svg>
                          ) : (
                            <svg
                              className="w-4 h-4 text-gray-300"
                              fill="currentColor"
                              viewBox="0 0 20 20"
                            >
                              <path
                                fillRule="evenodd"
                                d="M10 18a8 8 0 100-16 8 8 0 000 16zm0-2a6 6 0 100-12 6 6 0 000 12z"
                                clipRule="evenodd"
                              />
                            </svg>
                          )}
                        </div>
                        <div
                          className={`text-sm ${
                            isCheckpointDone
                              ? "text-gray-800 dark:text-white"
                              : "text-gray-500"
                          }`}
                        >
                          {CheckpointLabels[checkpoint]}
                        </div>
                      </div>
                    );
                  })}
                </div>

                {isCompletedMilestone && (
                  <div className="mt-3 text-xs text-green-500 dark:text-green-400">
                    ✓ All checkpoints for this milestone are complete!
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Debug info for development */}
        {process.env.NODE_ENV === "development" && (
          <div className="mt-4 p-2 border border-gray-200 rounded text-xs">
            <div className="font-bold mb-1">Journey State:</div>
            <div>Milestone: {milestone}</div>
            <div>Status: {status}</div>
            <div>Completed: {completed_checkpoints.join(", ")}</div>
          </div>
        )}
      </div>
    </div>
  );
}
