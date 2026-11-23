/**
 * The Box parent token for the portal, from a Client Credentials Grant through the
 * Portal_Box named credential. The client ID and secret live in the Portal_Box external
 * credential and are merged into the request body by Salesforce at callout time, so this
 * class only ever holds placeholders. Ported from unofficialbox/box-agentic-loans.
 *
 * The parent token never leaves the server: callers either use it for server-side reads
 * or exchange it for a token downscoped to one folder or file.
 */
public with sharing class PortalBoxAuth {
    @TestVisible
    private static final String TOKEN_ENDPOINT = 'callout:Portal_Box/oauth2/token';
    private static final String CACHE_KEY_PREFIX = 'PortalBoxParentToken';
    private static final Integer CACHE_SAFETY_MARGIN_SECONDS = 300;

    /**
     * Parent token for the configured subject, or null when Box refuses or nothing is configured.
     * A Box user ID on Portal_Box_Config__c acts as that user (inheriting the user's access);
     * otherwise the Enterprise ID yields a service account, which must be collaborated onto
     * the record folders.
     */
    public static String parentToken() {
        Portal_Box_Config__c config = Portal_Box_Config__c.getOrgDefaults();
        if (config == null) {
            return null;
        }
        Boolean asUser = String.isNotBlank(config.Box_User_Id__c);
        String subjectType = asUser ? 'user' : 'enterprise';
        String subjectId = asUser ? config.Box_User_Id__c : config.Enterprise_Id__c;
        if (String.isBlank(subjectId)) {
            return null;
        }
        String cacheKey = CACHE_KEY_PREFIX + subjectType + subjectId;
        String cached = cacheGet(cacheKey);
        if (String.isNotBlank(cached)) {
            return cached;
        }
        HttpResponse res = post(
            'grant_type=client_credentials'
            + '&client_id={!$Credential.Portal_Box.ClientId}'
            + '&client_secret={!$Credential.Portal_Box.ClientSecret}'
            + '&box_subject_type=' + subjectType
            + '&box_subject_id=' + EncodingUtil.urlEncode(subjectId, 'UTF-8')
        );
        if (res.getStatusCode() != 200) {
            return null;
        }
        Map<String, Object> body = (Map<String, Object>) JSON.deserializeUntyped(res.getBody());
        String token = (String) body.get('access_token');
        Integer expiresIn = body.get('expires_in') == null ? 0 : Integer.valueOf(body.get('expires_in'));
        cachePut(cacheKey, token, expiresIn);
        return token;
    }

    /** Form-encoded POST to the Box token endpoint through the named credential. */
    public static HttpResponse post(String body) {
        HttpRequest req = new HttpRequest();
        req.setEndpoint(TOKEN_ENDPOINT);
        req.setMethod('POST');
        req.setHeader('Content-Type', 'application/x-www-form-urlencoded');
        req.setTimeout(20000);
        req.setBody(body);
        return new Http().send(req);
    }

    /** Authenticated Box API GET with the parent token. */
    public static HttpResponse get(String path, String parentToken) {
        HttpRequest req = new HttpRequest();
        req.setEndpoint('callout:Portal_Box/2.0/' + path);
        req.setMethod('GET');
        req.setHeader('Authorization', 'Bearer ' + parentToken);
        req.setTimeout(20000);
        return new Http().send(req);
    }

    private static String cacheGet(String cacheKey) {
        try {
            return (String) Cache.Org.get(cacheKey);
        } catch (Exception e) {
            return null;
        }
    }

    private static void cachePut(String cacheKey, String token, Integer expiresIn) {
        Integer ttl = expiresIn - CACHE_SAFETY_MARGIN_SECONDS;
        if (String.isBlank(token) || ttl < 60) {
            return;
        }
        try {
            Cache.Org.put(cacheKey, token, Math.min(ttl, 28800));
        } catch (Exception e) {
            // No org cache partition: every request re-grants.
        }
    }
}
