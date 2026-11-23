/**
 * Portal Box settings, written by scripts/build_portal.py from config/salesforce/portal.json.
 * Edit that file and rebuild; do not edit the rendered class.
 */
public inherited sharing class PortalBoxSettings {
    /** Salesforce object the portal shows; its record ID selects the Box folder. */
    public static final String RECORD_OBJECT = '__RECORD_OBJECT__';
    /** Field on the record holding the customer's Account ID, or blank to rely on sharing alone. */
    public static final String ACCOUNT_FIELD = '__ACCOUNT_FIELD__';
    /** Subfolders of the record folder that customers may see. Empty means files at the folder root. */
    public static final List<String> VISIBLE_SUBFOLDERS = new List<String>{ __VISIBLE_SUBFOLDERS__ };
    /** Subfolder that receives customer uploads, or blank for the record folder root. */
    public static final String UPLOAD_SUBFOLDER = '__UPLOAD_SUBFOLDER__';
    /** Record field holding the signer's Box Sign iframe URL, or blank when Sign is off. */
    public static final String SIGN_EMBED_URL_FIELD = '__SIGN_EMBED_URL_FIELD__';
    /** Record field holding the Box Sign request ID, or blank when Sign is off. */
    public static final String SIGN_REQUEST_ID_FIELD = '__SIGN_REQUEST_ID_FIELD__';

    public static Boolean signEnabled() {
        return String.isNotBlank(SIGN_EMBED_URL_FIELD) && String.isNotBlank(SIGN_REQUEST_ID_FIELD);
    }
}
