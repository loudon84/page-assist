import { OctopSessionProvider } from "@/hooks/octop/OctopSessionContext"
import { EnterpriseGate } from "./EnterpriseGate"
import { EnterpriseShell } from "./EnterpriseShell"

export const EnterpriseRoot = () => {
  return (
    <OctopSessionProvider>
      <EnterpriseGate>
        <EnterpriseShell />
      </EnterpriseGate>
    </OctopSessionProvider>
  )
}
