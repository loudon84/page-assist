import { Alert } from "antd"

type Props = {
  marker:
    | "unconfigured"
    | "signed_out"
    | "expired"
    | "connecting"
    | "offline"
    | "peer_offline"
    | "empty"
    | "forbidden"
    | "approval_external"
    | "unknown"
    | "stop_unconfirmed"
    | "error"
  message: string
}

export const StateBanner = ({ marker, message }: Props) => {
  const type =
    marker === "empty"
      ? "info"
      : marker === "connecting"
        ? "info"
        : marker === "error" || marker === "forbidden"
          ? "error"
          : "warning"
  return (
    <Alert
      data-state-marker={marker}
      type={type}
      showIcon
      message={message}
      className="mb-3"
    />
  )
}
