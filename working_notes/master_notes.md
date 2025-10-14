
SQLAlchemy for defining data models as classes

pydantic for defining API transaction contract

fastAPI (instead of flask) for defining endpoints

---------------------------------------


10/13

created init db script


    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Database is already created by POSTGRES_DB env var

    EOSQL means -> Heredoc
    lets you write multi-line input directly in a script
    everything between <<-EOSQL and EOSQL get passed as input to the command

    << - take the following line as input
    - allow leading tabs
    
    Delimitters:
        EOSQL - delimiter, end of SQL
        EOF
    
    benefits of uing Heredoc

        multiline input without escaping
        readable sql - looks like sql
        vars get expanded ($postgres_db becomes the actual value)
        everything can go in one file


------------------

CI/CD pipeline


created /github
create /github/workflows -> ci-cd.yml
    set up workflow to run on push or pull of main
    job to run is 'test'
        services to test: 
            postgres

create dockerhub repo for project
app image pushed to dockerhub
created access key 
added username and access key to gh repo secrets
