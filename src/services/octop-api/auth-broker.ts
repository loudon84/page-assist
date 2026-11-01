export type AuthBroker = {
  getRedirectURL(provider: "octop"): string
  launchWebAuthFlow(details: {
    url: string
    interactive: boolean
  }): Promise<string>
  sessionGet(key: string): Promise<string | undefined>
  sessionSet(key: string, value: string): Promise<void>
  sessionRemove(key: string): Promise<void>
}

const sessionStore = (): typeof chrome.storage.session => {
  if (!chrome.storage?.session) {
    throw new Error("storage.session is required")
  }
  return chrome.storage.session
}

export const createChromeAuthBroker = (): AuthBroker => ({
  getRedirectURL(provider: "octop"): string {
    return chrome.identity.getRedirectURL(provider)
  },
  launchWebAuthFlow(details): Promise<string> {
    return new Promise((resolve, reject) => {
      chrome.identity.launchWebAuthFlow(
        { url: details.url, interactive: details.interactive },
        (redirectUrl) => {
          if (chrome.runtime.lastError || !redirectUrl) {
            reject(new Error(chrome.runtime.lastError?.message || "AUTH_CANCELLED"))
            return
          }
          resolve(redirectUrl)
        }
      )
    })
  },
  async sessionGet(key) {
    const bag = await sessionStore().get(key)
    return bag[key] as string | undefined
  },
  async sessionSet(key, value) {
    await sessionStore().set({ [key]: value })
  },
  async sessionRemove(key) {
    await sessionStore().remove(key)
  }
})

let broker: AuthBroker = createChromeAuthBroker()

export const getAuthBroker = (): AuthBroker => broker

export const setAuthBroker = (next: AuthBroker): void => {
  broker = next
}
