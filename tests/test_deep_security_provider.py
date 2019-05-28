import uuid
import boto3
import logging
from provider import handler

logging.basicConfig(level=logging.INFO)


def test_crud():
    response = {"PhysicalResourceId": "could-not-create"}
    try:
        name = "u{}".format(uuid.uuid4())
        context = {
            "name": name,
            "description": f"test {name}",
            "minimumAgentVersion": "6.0.0.0",
            "localConnectionsEnabled": True,
            "remoteConnectionsEnabled": True,
            "noConnectionEnabled": True,
            "noInternetEnabled": True,
            "restrictedInterfacesEnabled": True,
        }
        request = Request("Create", "Context", context)
        response = handler(request, {})
        assert response["Status"] == "SUCCESS", response["Reason"]
        assert "PhysicalResourceId" in response
        assert response["PhysicalResourceId"] is not None

        context["localConnectionsEnabled"] = False
        request = Request("Update", "Context", context, response["PhysicalResourceId"])
        response = handler(request, {})
        assert response["Status"] == "SUCCESS", response["Reason"]
        assert "PhysicalResourceId" in response
        assert response["PhysicalResourceId"] is not None
    finally:
        request = Request("Delete", "Context", {}, response["PhysicalResourceId"])
        response = handler(request, {})
        assert response["Status"] == "SUCCESS", response["Reason"]


def test_system_settings():
    request = Request("Create", "SystemSetting", system_setting)
    response = handler(request, {})
    assert response["Status"] == "SUCCESS", response["Reason"]

    request = Request("Update", "SystemSetting", system_setting, response['PhysicalResourceId'])
    response = handler(request, {})
    assert response["Status"] == "SUCCESS", response["Reason"]


class Request(dict):
    def __init__(self, request_type, resource_type, value, physical_resource_id=None):
        request_id = "request-%s" % uuid.uuid4()
        self.update(
            {
                "RequestType": request_type,
                "ResponseURL": "https://httpbin.org/put",
                "StackId": "arn:aws:cloudformation:us-west-2:EXAMPLE/stack-name/guid",
                "RequestId": request_id,
                "ResourceType": f"Custom::DeepSecurity{resource_type}",
                "LogicalResourceId": f"MyCustom{resource_type}",
                "ResourceProperties": {"Value": value},
            }
        )

        if physical_resource_id:
            self["PhysicalResourceId"] = physical_resource_id

system_setting = {
        "platformSettingSamlIdentityProviderCertificateExpiryWarningDays": {
            "value": "30"
        },
        "platformSettingUpdateAgentSecurityOnMissingDeepSecurityManagerEnabled": {
            "value": "true"
        },
        "platformSettingDdanManualSourceServerUrl": {
            "value": ""
        },
        "platformSettingSmartProtectionFeedbackThreatDetectionsThreshold": {
            "value": "10"
        },
        "intrusionPreventionSettingEventRankSeverityFilterMedium": {
            "value": "25"
        },
        "firewallSettingIntranetConnectivityTestExpectedContentRegex": {
            "value": ""
        },
        "platformSettingEventForwardingSnsEnabled": {
            "value": "false"
        },
        "platformSettingTenantAutoRevokeImpersonationByPrimaryTenantTimeout": {
            "value": "4 Hours"
        },
        "webReputationSettingEventRankRiskBlockedByAdministratorRank": {
            "value": "100"
        },
        "antiMalwareSettingEventEmailRecipients": {
            "value": ""
        },
        "firewallSettingIntranetConnectivityTestUrl": {
            "value": ""
        },
        "platformSettingTenantUseDefaultRelayGroupFromPrimaryTenantEnabled": {
            "value": "true"
        },
        "platformSettingExportedDiagnosticPackageLocale": {
            "value": "en_US"
        },
        "intrusionPreventionSettingEventRankSeverityFilterCritical": {
            "value": "100"
        },
        "platformSettingDemoModeEnabled": {
            "value": "false"
        },
        "platformSettingManagedDetectResponseCompanyGuid": {
            "value": ""
        },
        "platformSettingAlertDefaultEmailAddress": {
            "value": ""
        },
        "platformSettingAgentInitiatedActivationReactivateClonedEnabled": {
            "value": "true"
        },
        "platformSettingManagedDetectResponseServerUrl": {
            "value": ""
        },
        "platformSettingSyslogConfigId": {
            "value": "0"
        },
        "platformSettingSmtpStartTlsEnabled": {
            "value": "false"
        },
        "platformSettingUserPasswordRequireLettersAndNumbersEnabled": {
            "value": "true"
        },
        "platformSettingManagedDetectResponseEnabled": {
            "value": "false"
        },
        "platformSettingUpdateRulesPolicyAutoApplyEnabled": {
            "value": "true"
        },
        "platformSettingUserPasswordRequireNotSameAsUsernameEnabled": {
            "value": "false"
        },
        "logInspectionSettingEventRankSeverityMedium": {
            "value": "25"
        },
        "antiMalwareSettingRetainEventDuration": {
            "value": "7 Days"
        },
        "platformSettingUpdateAgentSecurityContactPrimarySourceOnMissingRelayEnabled": {
            "value": "true"
        },
        "firewallSettingEventRankSeverityLogOnly": {
            "value": "1"
        },
        "applicationControlSettingRetainEventDuration": {
            "value": "7 Days"
        },
        "platformSettingSystemEventForwardingSnmpPort": {
            "value": "162"
        },
        "firewallSettingEventRankSeverityDeny": {
            "value": "100"
        },
        "intrusionPreventionSettingEventRankSeverityFilterLow": {
            "value": "1"
        },
        "platformSettingManagedDetectResponseServiceToken": {
            "value": ""
        },
        "logInspectionSettingRetainEventDuration": {
            "value": "7 Days"
        },
        "platformSettingTenantAutoRevokeImpersonationByPrimaryTenantEnabled": {
            "value": "false"
        },
        "antiMalwareSettingEventEmailBodyTemplate": {
            "value": ""
        },
        "platformSettingRetainSecurityUpdatesMax": {
            "value": "10"
        },
        "platformSettingConnectedThreatDefenseControlManagerSourceOption": {
            "value": "Manually select an Apex Central server"
        },
        "antiMalwareSettingEventEmailEnabled": {
            "value": "false"
        },
        "platformSettingRecommendationOngoingScansEnabled": {
            "value": "No"
        },
        "platformSettingUserPasswordLengthMin": {
            "value": "8"
        },
        "platformSettingAwsManagerIdentityUseInstanceRoleEnabled": {
            "value": "true"
        },
        "platformSettingAlertAgentUpdatePendingThreshold": {
            "value": "7 Days"
        },
        "platformSettingUserPasswordRequireSpecialCharactersEnabled": {
            "value": "false"
        },
        "platformSettingUpdateApplianceDefaultAgentVersion": {
            "value": ""
        },
        "platformSettingSystemEventForwardingSnmpEnabled": {
            "value": "false"
        },
        "platformSettingSmtpBounceEmailAddress": {
            "value": ""
        },
        "platformSettingUpdateRelaySecuritySupportAgent9AndEarlierEnabled": {
            "value": "false"
        },
        "platformSettingManagedDetectResponseProxyId": {
            "value": ""
        },
        "platformSettingInactiveAgentCleanupEnabled": {
            "value": "false"
        },
        "platformSettingUserSessionIdleTimeout": {
            "value": "30 Minutes"
        },
        "antiMalwareSettingEventEmailSubject": {
            "value": ""
        },
        "platformSettingConnectedThreatDefenseControlManagerUseProxyEnabled": {
            "value": "false"
        },
        "platformSettingAwsManagerIdentityAccessKey": {
            "value": ""
        },
        "platformSettingConnectedThreatDefenseControlManagerProxyId": {
            "value": ""
        },
        "platformSettingTenantAllowImpersonationByPrimaryTenantEnabled": {
            "value": "false"
        },
        "platformSettingConnectedThreatDefenseControlManagerManualSourceServerUrl": {
            "value": ""
        },
        "platformSettingUserPasswordRequireMixedCaseEnabled": {
            "value": "true"
        },
        "platformSettingSmartProtectionFeedbackForSuspiciousFileEnabled": {
            "value": "true"
        },
        "platformSettingSmartProtectionFeedbackIndustryType": {
            "value": "Not specified"
        },
        "webReputationSettingRetainEventDuration": {
            "value": "7 Days"
        },
        "integrityMonitoringSettingEventRankSeverityMedium": {
            "value": "25"
        },
        "platformSettingUpdateRelaySecurityAllRegionsPatternsDownloadEnabled": {
            "value": "false"
        },
        "platformSettingDdanSubmissionEnabled": {
            "value": "false"
        },
        "webReputationSettingEventRankRiskSuspicious": {
            "value": "25"
        },
        "integrityMonitoringSettingEventRankSeverityCritical": {
            "value": "100"
        },
        "platformSettingSmtpFromEmailAddress": {
            "value": ""
        },
        "platformSettingEventForwardingSnsTopicArn": {
            "value": ""
        },
        "firewallSettingInternetConnectivityTestExpectedContentRegex": {
            "value": ""
        },
        "platformSettingConnectedThreatDefenseControlManagerManualSourceApiKey": {
            "value": ""
        },
        "platformSettingUpdateSecurityPrimarySourceMode": {
            "value": "Trend Micro ActiveUpdate Server"
        },
        "webReputationSettingEventRankRiskDangerous": {
            "value": 100
        },
        "platformSettingUserHideUnlicensedModulesEnabled": {
            "value": False
        },
        "platformSettingCaptureEncryptedTrafficEnabled": {
            "value": "false"
        },
        "hostedServicesSettingAwsMeteredBillingCustomBillingEnabled": {
            "value": "false"
        },
        "platformSettingRetainSystemEventDuration": {
            "value": "53 Weeks"
        },
        "platformSettingUserPasswordExpiry": {
            "value": "Never"
        },
        "platformSettingSmartProtectionFeedbackEnabled": {
            "value": "false"
        },
        "integrityMonitoringSettingRetainEventDuration": {
            "value": "7 Days"
        },
        "logInspectionSettingEventRankSeverityCritical": {
            "value": "100"
        },
        "platformSettingDdanProxyId": {
            "value": ""
        },
        "platformSettingAgentInitiatedActivationWithinIpListId": {
            "value": ""
        },
        "platformSettingUpdateSecurityPrimarySourceUrl": {
            "value": "http://"
        },
        "platformSettingAgentlessVcloudProtectionEnabled": {
            "value": "false"
        },
        "platformSettingActiveSessionsMaxExceededAction": {
            "value": "Block new sessions"
        },
        "platformSettingUpdateHostnameOnIpChangeEnabled": {
            "value": "false"
        },
        "logInspectionSettingEventRankSeverityHigh": {
            "value": "50"
        },
        "platformSettingSmtpRequiresAuthenticationEnabled": {
            "value": "false"
        },
        "hostedServicesSettingAwsMeteredBillingCustomBillingUrl": {
            "value": ""
        },
        "platformSettingActiveSessionsMax": {
            "value": "10"
        },
        "logInspectionSettingEventRankSeverityLow": {
            "value": "1"
        },
        "platformSettingSmtpUsername": {
            "value": ""
        },
        "platformSettingEventForwardingSnsAdvancedConfigEnabled": {
            "value": "false"
        },
        "firewallSettingInternetConnectivityTestInterval": {
            "value": "10 Seconds"
        },
        "platformSettingWhoisUrl": {
            "value": ""
        },
        "platformSettingDdanSourceOption": {
            "value": "Manually select a Deep Discovery Analyzer server"
        },
        "platformSettingConnectedThreatDefenseControlManagerSuspiciousObjectListComparisonEnabled": {
            "value": "false"
        },
        "platformSettingExportedFileCharacterEncoding": {
            "value": "UTF-8"
        },
        "platformSettingUserSessionDurationMax": {
            "value": "No Limit"
        },
        "platformSettingUpdateSoftwareAlternateUpdateServerUrls": {
            "value": ""
        },
        "platformSettingRetainCountersDuration": {
            "value": "13 Weeks"
        },
        "platformSettingSmartProtectionFeedbackInterval": {
            "value": "5"
        },
        "platformSettingSystemEventForwardingSnmpAddress": {
            "value": ""
        },
        "platformSettingSmtpServerAddress": {
            "value": ""
        },
        "platformSettingSmtpPassword": {
            "value": ""
        },
        "platformSettingEventForwardingSnsConfigJson": {
            "value": ""
        },
        "firewallSettingRetainEventDuration": {
            "value": "7 Days"
        },
        "webReputationSettingEventRankRiskUntested": {
            "value": "25"
        },
        "platformSettingManagedDetectResponseUseProxyEnabled": {
            "value": "false"
        },
        "platformSettingEventForwardingSnsSecretKey": {
            "value": ""
        },
        "platformSettingAwsManagerIdentitySecretKey": {
            "value": ""
        },
        "webReputationSettingEventRankRiskHighlySuspicious": {
            "value": "50"
        },
        "platformSettingUserPasswordExpirySendEmailEnabled": {
            "value": "false"
        },
        "platformSettingUserSignInAttemptsAllowedNumber": {
            "value": "5"
        },
        "platformSettingDdanUseProxyEnabled": {
            "value": "false"
        },
        "platformSettingAgentInitiatedActivationEnabled": {
            "value": "For any computers"
        },
        "platformSettingSmartProtectionFeedbackBandwidthMaxKbytes": {
            "value": "32"
        },
        "firewallSettingEventRankSeverityPacketRejection": {
            "value": "50"
        },
        "platformSettingManagedDetectResponseUsePrimaryTenantSettingsEnabled": {
            "value": "false"
        },
        "platformSettingEventForwardingSnsAccessKey": {
            "value": ""
        },
        "platformSettingAgentInitiatedActivationSpecifyHostnameEnabled": {
            "value": "true"
        },
        "platformSettingConnectedThreatDefensesUsePrimaryTenantServerSettingsEnabled": {
            "value": "false"
        },
        "platformSettingInactiveAgentCleanupDuration": {
            "value": "1 Month"
        },
        "platformSettingAgentInitiatedActivationDuplicateHostnameMode": {
            "value": "Re-activate the existing Computer"
        },
        "platformSettingAgentInitiatedActivationReactivateUnknownEnabled": {
            "value": "true"
        },
        "platformSettingAgentInitiatedActivationPolicyId": {
            "value": ""
        },
        "platformSettingRetainAgentInstallersPerPlatformMax": {
            "value": "5"
        },
        "applicationControlSettingServeRulesetsFromRelaysEnabled": {
            "value": "false"
        },
        "integrityMonitoringSettingEventRankSeverityHigh": {
            "value": "50"
        },
        "platformSettingSamlRetainInactiveExternalAdministratorsDuration": {
            "value": "365"
        },
        "intrusionPreventionSettingRetainEventDuration": {
            "value": "7 Days"
        },
        "firewallSettingInternetConnectivityTestUrl": {
            "value": ""
        },
        "platformSettingProxyAgentUpdateProxyId": {
            "value": ""
        },
        "platformSettingDdanAutoSubmissionEnabled": {
            "value": "false"
        },
        "platformSettingDdanManualSourceApiKey": {
            "value": ""
        },
        "intrusionPreventionSettingEventRankSeverityFilterError": {
            "value": "100"
        },
        "intrusionPreventionSettingEventRankSeverityFilterHigh": {
            "value": "50"
        },
        "integrityMonitoringSettingEventRankSeverityLow": {
            "value": "1"
        }
    }

