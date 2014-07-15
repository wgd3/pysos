class Task():

    uuid = ""
    action_type = ""
    status = ""
    command_id = ""

    schema31 = {
        "uuid": 0,
        "action_type": 1,
        "status": 2,
        "command_id": 7,
    }
    schema32 = {
        "uuid": 0,
        "action_type": 1,
        "status": 2,
        "command_id": 7,
    }
    schema33 = {
        "uuid": 0,
        "action_type": 1,
        "status": 2,
        "command_id": 7,
    }
    schema34 = {
        "uuid": 0,
        "action_type": 1,
        "status": 2,
        "command_id": 7,
    }

    statuses = {
        "0": "Unknown - task doesn't exist",
        "1": "Init - task hasn't started yet",
        "2": "Working - task is running",
        "3": "Finished - task finished successfully",
        "4": "Aborting - task ended in failure",
        "5": "Cleaning - clean up due to failure or stopTask request"
    }

    codes = {
        "0": "Unknown",
        "1": "AddVm",
        "2": "AddVmFromTemplate",
        "3": "AddVmFromScratch",
        "4": "RemoveVm",
        "5": "UpdateVm",
        "6": "RebootVm",
        "7": "StopVm",
        "8": "ShutdownVm",
        "9": "ChangeDisk",
        "10": "PauseVm",
        "11": "HibernateVm",
        "12": "RunVm",
        "13": "RunVmOnce",
        "14": "MigrateVm",
        "15": "InternalMigrateVm",
        "16": "MigrateVmToServer",
        "18": "VmLogon",
        "22": "SetVmTicket",
        "23": "ExportVm",
        "24": "ExportVmTemplate",
        "25": "RestoreStatelessVm",
        "28": "AddVmInterface",
        "29": "RemoveVmInterface",
        "30": "UpdateVmInterface",
        "128": "ReorderVmNics",
        "31": "AddDisk",
        "32": "RegisterDisk",
        "33": "MoveVm",
        "34": "UpdateVmDisk",
        "180": "AttachDiskToVm",
        "181": "DetachDiskFromVm",
        "182": "HotPlugDiskToVm",
        "183": "HotUnPlugDiskFromVm",
        "184": "HotSetNumberOfCpus",
        "35": "ChangeFloppy",
        "36": "ImportVm",
        "37": "RemoveVmFromImportExport",
        "38": "RemoveVmTemplateFromImportExport",
        "39": "ImportVmTemplate",
        "40": "ChangeVMCluster",
        "41": "CancelMigrateVm",
        "42": "ActivateDeactivateVmNic",
        "52": "AddVmFromSnapshot",
        "53": "CloneVm",
        "43": "ImportVmFromConfiguration",
        "44": "UpdateVmVersion",
        "45": "ImportVmTemplateFromConfiguration",
        "46": "ProcessDownVm",
        "100": "ProvisionVds",
        "101": "AddVds",
        "102": "UpdateVds",
        "103": "RemoveVds",
        "104": "RestartVds",
        "105": "VdsNotRespondingTreatment",
        "106": "MaintenanceVds",
        "107": "MaintenanceNumberOfVdss",
        "108": "ActivateVds",
        "109": "InstallVdsInternal",
        "110": "ClearNonResponsiveVdsVms",
        "112": "ApproveVds",
        "114": "HandleVdsCpuFlagsOrClusterChanged",
        "115": "InitVdsOnUp",
        "117": "SetNonOperationalVds",
        "119": "AddVdsSpmId",
        "120": "ForceSelectSPM",
        "121": "StartVds",
        "122": "StopVds",
        "124": "HandleVdsVersion",
        "125": "ChangeVDSCluster",
        "126": "RefreshHostCapabilities",
        "127": "SshSoftFencing",
        "128": "VdsPowerDown",
        "129": "UpgradeOvirtNodeInternal",
        "130": "InstallVds",
        "131": "UpgradeOvirtNode",
        "132": "VdsKdumpDetection",
        "149": "UpdateNetworkToVdsInterface",
        "150": "AttachNetworkToVdsInterface",
        "151": "DetachNetworkFromVdsInterface",
        "152": "AddBond",
        "153": "RemoveBond",
        "154": "AddNetwork",
        "155": "RemoveNetwork",
        "156": "UpdateNetwork",
        "157": "CommitNetworkChanges",
        "158": "SetupNetworks",
        "159": "PersistentSetupNetworks",
        "160": "AddVnicProfile",
        "161": "UpdateVnicProfile",
        "162": "RemoveVnicProfile",
        "163": "LabelNetwork",
        "164": "UnlabelNetwork",
        "165": "LabelNic",
        "166": "UnlabelNic",
        "170": "AddVmNumaNodes",
        "171": "UpdateVmNumaNodes",
        "172": "RemoveVmNumaNodes",
        "201": "AddVmTemplate",
        "202": "UpdateVmTemplate",
        "203": "RemoveVmTemplate",
        "226": "MoveOrCopyTemplate",
        "220": "AddVmTemplateInterface",
        "221": "RemoveVmTemplateInterface",
        "222": "UpdateVmTemplateInterface",
        "204": "TryBackToSnapshot",
        "205": "RestoreFromSnapshot",
        "206": "CreateAllSnapshotsFromVm",
        "207": "CreateSnapshot",
        "208": "CreateSnapshotFromTemplate",
        "209": "CreateImageTemplate",
        "210": "RemoveSnapshot",
        "211": "RemoveImage",
        "212": "RemoveAllVmImages",
        "213": "AddImageFromScratch",
        "215": "RemoveTemplateSnapshot",
        "216": "RemoveAllVmTemplateImageTemplates",
        "223": "TryBackToAllSnapshotsOfVm",
        "224": "RestoreAllSnapshots",
        "225": "CopyImageGroup",
        "226": "MoveOrCopyDisk",
        "227": "RemoveSnapshotSingleDisk",
        "229": "CreateCloneOfTemplate",
        "230": "RemoveDisk",
        "231": "MoveImageGroup",
        "232": "GetDiskAlignment",
        "233": "RemoveVmHibernationVolumes",
        "234": "RemoveMemoryVolumes",
        "235": "RemoveDiskSnapshots",
        "236": "RemoveSnapshotSingleDiskLive",
        "237": "Merge",
        "238": "MergeStatus",
        "239": "DestroyImage",
        "301": "AddVmPool",
        "304": "AddVmPoolWithVms",
        "303": "UpdateUserVm",
        "305": "UpdateVmPoolWithVms",
        "306": "AddVmAndAttachToPool",
        "307": "RemoveVmPool",
        "312": "DetachUserFromVmFromPool",
        "313": "AddVmToPool",
        "314": "RemoveVmFromPool",
        "318": "AttachUserToVmFromPoolAndRun",
        "406": "LoginUser",
        "408": "LogoutUser",
        "410": "LogoutBySession",
        "409": "RemoveUser",
        "415": "RemoveGroup",
        "416": "ChangeUserPassword",
        "418": "LoginAdminUser",
        "419": "AddUser",
        "420": "AddGroup",
        "501": "AddTag",
        "502": "RemoveTag",
        "503": "UpdateTag",
        "504": "MoveTag",
        "505": "AttachUserToTag",
        "506": "DetachUserFromTag",
        "507": "AttachUserGroupToTag",
        "508": "DetachUserGroupFromTag",
        "509": "AttachVmsToTag",
        "510": "DetachVmFromTag",
        "511": "AttachVdsToTag",
        "512": "DetachVdsFromTag",
        "515": "UpdateTagsVmMapDefaultDisplayType",
        "516": "AttachTemplatesToTag",
        "517": "DetachTemplateFromTag",
        "601": "AddQuota",
        "602": "UpdateQuota",
        "603": "RemoveQuota",
        "604": "ChangeQuotaForDisk",
        "701": "AddBookmark",
        "702": "RemoveBookmark",
        "703": "UpdateBookmark",
        "704": "AddVdsGroup",
        "705": "UpdateVdsGroup",
        "706": "RemoveVdsGroup",
        "708": "AttachNetworkToVdsGroup",
        "709": "DetachNetworkToVdsGroup",
        "711": "UpdateNetworkOnCluster",
        "712": "AttachNetworksToCluster",
        "713": "DetachNetworksFromCluster",
        "800": "AddPermission",
        "801": "RemovePermission",
        "803": "UpdateRole",
        "804": "RemoveRole",
        "805": "AttachActionGroupsToRole",
        "806": "DetachActionGroupsFromRole",
        "809": "AddRoleWithActionGroups",
        "811": "AddSystemPermission",
        "812": "RemoveSystemPermission",
        "916": "AddLocalStorageDomain",
        "902": "AddNFSStorageDomain",
        "903": "UpdateStorageDomain",
        "904": "RemoveStorageDomain",
        "905": "ForceRemoveStorageDomain",
        "906": "AttachStorageDomainToPool",
        "907": "DetachStorageDomainFromPool",
        "908": "ActivateStorageDomain",
        "916": "ConnectDomainToStorage",
        "909": "DeactivateStorageDomain",
        "910": "AddSANStorageDomain",
        "911": "ExtendSANStorageDomain",
        "913": "ReconstructMasterDomain",
        "915": "RecoveryStoragePool",
        "950": "AddEmptyStoragePool",
        "951": "AddStoragePoolWithStorages",
        "957": "RemoveStoragePool",
        "958": "UpdateStoragePool",
        "959": "FenceVdsManualy",
        "960": "AddExistingFileStorageDomain",
        "1000": "AddStorageServerConnection",
        "1001": "UpdateStorageServerConnection",
        "1002": "DisconnectStorageServerConnection",
        "1003": "RemoveStorageServerConnection",
        "1004": "ConnectHostToStoragePoolServers",
        "1005": "DisconnectHostFromStoragePoolServers",
        "1006": "ConnectStorageToVds",
        "1007": "SetStoragePoolStatus",
        "1008": "ConnectAllHostsToLun",
        "1009": "AddPosixFsStorageDomain",
        "1010": "LiveMigrateDisk",
        "1011": "LiveMigrateVmDisks",
        "1012": "MoveDisks",
        "1013": "ExtendImageSize",
        "1014": "ImportRepoImage",
        "1015": "ExportRepoImage",
        "1016": "AttachStorageConnectionToStorageDomain",
        "1017": "DetachStorageConnectionFromStorageDomain",
        "1018": "SyncLunsInfoForBlockStorageDomain",
        "1100": "AddEventSubscription",
        "1101": "RemoveEventSubscription",
        "1301": "ReloadConfigurations",
        "1400": "CreateGlusterVolume",
        "1401": "SetGlusterVolumeOption",
        "1402": "StartGlusterVolume",
        "1403": "StopGlusterVolume",
        "1404": "ResetGlusterVolumeOptions",
        "1405": "DeleteGlusterVolume",
        "1406": "GlusterVolumeRemoveBricks",
        "1407": "StartRebalanceGlusterVolume",
        "1408": "ReplaceGlusterVolumeBrick",
        "1409": "AddBricksToGlusterVolume",
        "1410": "StartGlusterVolumeProfile",
        "1411": "StopGlusterVolumeProfile",
        "1412": "RemoveGlusterServer",
        "1413": "AddGlusterFsStorageDomain",
        "1414": "EnableGlusterHook",
        "1415": "DisableGlusterHook",
        "1416": "UpdateGlusterHook",
        "1417": "AddGlusterHook",
        "1418": "RemoveGlusterHook",
        "1419": "RefreshGlusterHooks",
        "1420": "ManageGlusterService",
        "1421": "StopRebalanceGlusterVolume",
        "1422": "StartRemoveGlusterVolumeBricks",
        "1423": "StopRemoveGlusterVolumeBricks",
        "1424": "CommitRemoveGlusterVolumeBricks",
        "1425": "RefreshGlusterVolumeDetails",
        "1450": "AddClusterPolicy",
        "1451": "EditClusterPolicy",
        "1452": "RemoveClusterPolicy",
        "1453": "RemoveExternalPolicyUnit",
        "1500": "AddExternalEvent",
        "1600": "AddProvider",
        "1601": "UpdateProvider",
        "1602": "RemoveProvider",
        "1603": "TestProviderConnectivity",
        "1604": "ImportProviderCertificateChain",
        "1605": "AddNetworkOnProvider",
        "1606": "AddSubnetToProvider",
        "1607": "RemoveSubnetFromProvider",
        "1700": "AddWatchdog",
        "1701": "UpdateWatchdog",
        "1702": "RemoveWatchdog",
        "1750": "AddNetworkQoS",
        "1751": "UpdateNetworkQoS",
        "1752": "RemoveNetworkQoS",
        "1800": "AddExternalJob",
        "1801": "EndExternalJob",
        "1802": "ClearExternalJob",
        "1803": "AddExternalStep",
        "1804": "EndExternalStep",
        "1850": "AddInternalJob",
        "1851": "AddInternalStep",
        "1900": "UpdateMomPolicy",
        "1901": "UploadStream",
        "1902": "ProcessOvfUpdateForStorageDomain",
        "1903": "CreateOvfVolumeForStorageDomain",
        "1904": "CreateOvfStoresForStorageDomain",
        "1950": "AddAffinityGroup",
        "1951": "EditAffinityGroup",
        "1952": "RemoveAffinityGroup",
        "2000": "AddIscsiBond",
        "2001": "EditIscsiBond",
        "2002": "RemoveIscsiBond",
        "2050": "SetHaMaintenance",
        "2150": "AddRngDevice",
        "2151": "UpdateRngDevice",
        "2152": "RemoveRngDevice",
        "2100": "RemoveAuditLogById",
        "2101": "ClearAllDismissedAuditLogs",
        "3000":	"SetDataOnSession",
    }

    def __init__(self, csvList, dbVersion):

        details = csvList

        current_schema = "3.3"   # arbitrary, just to set a default
        if dbVersion == "3.1":
            current_schema = self.schema31
        elif dbVersion == "3.2":
            current_schema = self.schema32
        elif dbVersion == "3.3":
            current_schema = self.schema33
        elif dbVersion == "3.4":
            current_schema = self.schema34

        if len(details) > 2:
            self.uuid = details[current_schema['uuid']]
            self.command_id = details[current_schema['command_id']]
            self.action_type = self.codes[details[current_schema['action_type']]]
            tempstatus = details[current_schema['status']]
            self.status = self.statuses[tempstatus]

    def get_action_type(self):
        return self.action_type

    def get_uuid(self):
        return self.uuid

    def get_status(self):
        return self.status

    def get_command_id(self):
        return self.command_id