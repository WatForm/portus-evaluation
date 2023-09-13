# portus-tests

1. Run the script get-expert-models.sh to download the expert models.

2. Update the syntax used in these models for Alloy 6
    
    `find . -name "*.als" | xargs sed '' "s/'/\"/g"` (on Mac)

    