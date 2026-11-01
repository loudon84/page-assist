import type { ConversationUiState } from "@/services/octop-api/types"

export const isBusyState = (state: ConversationUiState): boolean => {
  switch (state) {
    case "UPLOADING":
    case "SUBMITTING":
    case "RUNNING":
    case "CANCELLING":
    case "RECONCILING":
      return true
    case "EMPTY":
    case "CREATING":
    case "IDLE":
    case "AWAITING_APPROVAL":
    case "UNKNOWN":
      return false
    default: {
      const exhaustive: never = state
      return exhaustive
    }
  }
}

export const DEFAULT_QUESTION = "请分析这些材料。"
