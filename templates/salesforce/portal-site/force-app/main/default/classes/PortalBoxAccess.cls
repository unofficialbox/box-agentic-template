/**
 * Who may open a record's Box documents in the portal.
 *
 * The record must be visible to the signed-in user under sharing. When the portal config
 * names an account field, an external user must also belong to that account. Guests are
 * always refused. Every Box endpoint checks this before it touches the record's folder.
 */
public with sharing class PortalBoxAccess {
    @TestVisible private static String userTypeOverride;
    @TestVisible private static Id accountOverride;
    @TestVisible private static SObject recordOverride;

    public static Boolean isGuest() {
        return userType() == 'Guest';
    }

    /** The record, read with sharing, or null when the caller may not use it. */
    public static SObject record(Id recordId) {
        if (isGuest() || recordId == null
            || recordId.getSObjectType().getDescribe().getName() != PortalBoxSettings.RECORD_OBJECT) {
            return null;
        }
        if (Test.isRunningTest() && recordOverride != null) {
            return recordOverride.Id == recordId ? recordOverride : null;
        }
        List<String> fields = new List<String>{ 'Id' };
        if (String.isNotBlank(PortalBoxSettings.ACCOUNT_FIELD)) fields.add(PortalBoxSettings.ACCOUNT_FIELD);
        if (PortalBoxSettings.signEnabled()) {
            fields.add(PortalBoxSettings.SIGN_EMBED_URL_FIELD);
            fields.add(PortalBoxSettings.SIGN_REQUEST_ID_FIELD);
        }
        List<SObject> visible;
        try {
            visible = Database.query('SELECT ' + String.join(fields, ', ') + ' FROM '
                + String.escapeSingleQuotes(PortalBoxSettings.RECORD_OBJECT) + ' WHERE Id = :recordId LIMIT 1');
        } catch (QueryException denied) {
            return null;
        }
        if (visible.isEmpty()) return null;
        Id account = customerAccount();
        if (account != null && String.isNotBlank(PortalBoxSettings.ACCOUNT_FIELD)
            && visible[0].get(PortalBoxSettings.ACCOUNT_FIELD) != account) {
            return null;
        }
        return visible[0];
    }

    /** The external user's Account, or null for internal users. */
    public static Id customerAccount() {
        if (accountOverride != null) return accountOverride;
        try {
            return new IdentityReader().account();
        } catch (QueryException unavailable) {
            return null;
        }
    }

    private static String userType() {
        return userTypeOverride == null ? UserInfo.getUserType() : userTypeOverride;
    }

    private without sharing class IdentityReader {
        private Id account() {
            List<Schema.User> users = [SELECT Contact.AccountId FROM User WHERE Id = :UserInfo.getUserId()];
            return users.isEmpty() || users[0].Contact == null ? null : users[0].Contact.AccountId;
        }
    }
}
