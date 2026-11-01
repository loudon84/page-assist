import { EnterpriseGate } from "@/components/Octop/EnterpriseGate"
import { EnterpriseShell } from "@/components/Octop/EnterpriseShell"
import { ExpertCatalog } from "@/components/Octop/ExpertCatalog"
import { ExpertChat } from "@/components/Octop/ExpertChat"
import { LoginPage } from "@/components/Octop/LoginPage"
import { Navigate, Route, Routes } from "react-router-dom"

const EnterpriseRoutes = () => {
  return (
    <EnterpriseGate>
      <Routes>
        <Route element={<EnterpriseShell />}>
          <Route path="/enterprise" element={<Navigate to="/enterprise/experts" replace />} />
          <Route path="/enterprise/login" element={<LoginPage />} />
          <Route path="/enterprise/experts" element={<ExpertCatalog />} />
          <Route path="/enterprise/experts/:expertKey" element={<ExpertChat mode="new" />} />
          <Route
            path="/enterprise/experts/:expertKey/threads/:threadId"
            element={<ExpertChat mode="thread" />}
          />
        </Route>
      </Routes>
    </EnterpriseGate>
  )
}

export default EnterpriseRoutes
