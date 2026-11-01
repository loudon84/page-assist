import { Button, Form, Input, Switch, Typography } from "antd"
import { useEffect, useState } from "react"
import { SettingsLayout } from "@/components/Layouts/SettingsOptionLayout"
import {
  isEnterpriseBrowser,
  loadEnterpriseConfig,
  saveEnterpriseConfig
} from "@/services/octop-api"
import { getAuthBroker } from "@/services/octop-api/auth-broker"

const OptionEnterpriseSettings = () => {
  const [enabled, setEnabled] = useState(false)
  const [baseUrl, setBaseUrl] = useState("")
  const [clientId, setClientId] = useState("")
  const [saved, setSaved] = useState("")
  const redirect = isEnterpriseBrowser() ? getAuthBroker().getRedirectURL("octop") : ""

  useEffect(() => {
    void loadEnterpriseConfig().then((cfg) => {
      setEnabled(cfg.enabled)
      setBaseUrl(cfg.base_url)
      setClientId(cfg.client_id)
    })
  }, [])

  if (!isEnterpriseBrowser()) {
    return (
      <SettingsLayout>
        <Typography.Paragraph>Enterprise features are not available in Firefox.</Typography.Paragraph>
      </SettingsLayout>
    )
  }

  return (
    <SettingsLayout>
      <h2 className="text-base font-semibold leading-7 text-gray-900 dark:text-white">
        Enterprise / Octop
      </h2>
      <Form layout="vertical" className="mt-6 max-w-xl">
        <Form.Item label="Enable enterprise">
          <Switch checked={enabled} onChange={setEnabled} />
        </Form.Item>
        <Form.Item label="Server origin (HTTPS)">
          <Input value={baseUrl} onChange={(e) => setBaseUrl(e.target.value)} placeholder="https://octop.example.internal" />
        </Form.Item>
        <Form.Item label="Client ID">
          <Input value={clientId} onChange={(e) => setClientId(e.target.value)} />
        </Form.Item>
        <Form.Item label="Redirect URI (register this exactly on the server)">
          <Input value={redirect} readOnly />
        </Form.Item>
        <Button
          type="primary"
          onClick={async () => {
            await saveEnterpriseConfig({
              enabled,
              base_url: baseUrl,
              client_id: clientId,
              source: "user",
              allow_insecure_dev: false
            })
            setSaved("Saved")
          }}>
          Save
        </Button>
        {saved ? <span className="ml-3 text-green-600">{saved}</span> : null}
      </Form>
    </SettingsLayout>
  )
}

export default OptionEnterpriseSettings
