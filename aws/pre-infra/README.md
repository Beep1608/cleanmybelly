# pre-infrea

# How hosting by yourself this project on AWS?
## 1. Buinding "pre-infra" infraestructure
### Run the next comands
> You have to ensure that your are logged in your AWS account int your AWS CLI, you can verify this using `aws configure list`

> If you have to chose a different AWS region, you have to override this on  pre-infra/variables.tf

1. TODO: Draw up

    `cd pre-infra`

2. TODO: Draw up

    `terraform init`

3. TODO: Draw up

    `terraform plan -out plan.out`

    `terraform apply "plan.out"`

4. Save thes access key credentials for the programatic IAM user "terraform-deployer" 

    `terraform output -raw deployer_access_key_id`

    `terraform output -raw deployer_secret_access_key`

5. Save the bucket name for using this on /infra remote backend.

    `terraform output -raw terraform_state_bucket_name"`

## 2. Buinding "infra" infraestructure
### Setting the terraform-user
Now we going start to work with the programatic user who we just created.

1. Using the before access and secret keys run setting the `terraform-user`. This profile will be used on /infra/main.tf for setting this run:

    `aws configure --profile terraform-user`

    > For verifing that you've crated the profile correctly, you can run `aws configure list --profile terraform-user`

2. The we have to create the diferentes workspaces using:

    - Initialize the remote backend and download the provider

        `terraform init`
