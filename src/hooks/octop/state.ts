import type { ConversationUiState } from "@/services/octop-api/types"

export const isBusyState = (state: ConversationUiState): boolean => {
  switch (state) {
    case "CREATING":
    case "UPLOADING":
    case "SUBMITTING":
    case "RUNNING":
    case "AWAITING_APPROVAL":
    case "CANCELLING":
    case "RECONCILING":
      return true
    case "EMPTY":
    case "IDLE":
    case "UNKNOWN":
      return false
    default: {
      const exhaustive: never = state
      return exhaustive
    }
  }
}

export const DEFAULT_QUESTION = "请分析这些材料。"
