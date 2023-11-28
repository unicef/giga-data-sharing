package internal.giga.customSasProvider;

import org.apache.hadoop.fs.azurebfs.extensions.SASTokenProvider;

import java.io.IOException;
import java.security.AccessControlException;


public class CustomSasProvider implements SASTokenProvider {
    private String sasToken;

    @Override
    public void initialize(org.apache.hadoop.conf.Configuration configuration, String s) throws IOException {
        String sasToken = System.getenv("AZURE_SAS_TOKEN");
        if (sasToken == null) {
            throw new IOException("`AZURE_SAS_TOKEN` is not set");
        }

        this.sasToken = sasToken;
    }

    @Override
    public String getSASToken(String s, String s1, String s2, String s3) throws AccessControlException {
        return this.sasToken;
    }

    public static void main(String[] args) {
    }
}
