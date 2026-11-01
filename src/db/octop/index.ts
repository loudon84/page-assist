import Dexie, { type Table } from "dexie"
import { sha256Jcs } from "./hash"

export type OctopRecentRef = {
  id: string
  accountPartition: string
  kind: "expert" | "thread"
  expertKey: string
  threadId?: string
  updatedAt: number
}

export class PageAssistOctopDatabase extends Dexie {
  recentRefs!: Table<OctopRecentRef>

  constructor() {
    super("PageAssistOctopDatabase")
    this.version(1).stores({
      recentRefs: "id, accountPartition, expertKey, updatedAt"
    })
  }
}

export const octopDb = new PageAssistOctopDatabase()

export const accountPartition = async (input: {
  canonicalOrigin: string
  instance_id: string
  tenant_id: string
  subject: string
}): Promise<string> => {
  return sha256Jcs({
    v: 1,
    canonicalOrigin: input.canonicalOrigin,
    instance_id: input.instance_id,
    tenant_id: input.tenant_id,
    subject: input.subject
  })
}

export const saveRecent = async (ref: OctopRecentRef): Promise<void> => {
  await octopDb.recentRefs.put(ref)
}

export const listRecent = async (accountPartitionValue: string) => {
  return octopDb.recentRefs
    .where("accountPartition")
    .equals(accountPartitionValue)
    .reverse()
    .sortBy("updatedAt")
}

export const deletePartition = async (accountPartitionValue: string): Promise<void> => {
  await octopDb.recentRefs.where("accountPartition").equals(accountPartitionValue).delete()
}
