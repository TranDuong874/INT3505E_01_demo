git clone https://github.com/swagger-api/swagger-codegen
cd swagger-codegen

# install JDK
sudo apt-get update
sudo apt-get install -y openjdk-17-jdk
java -version

sudo apt-get install -y maven

mvn package

java -jar modules/swagger-codegen-cli/target/swagger-codegen-cli.jar generate \
  -i ~/none-382-b91-Product-1.0.0-resolved.yaml \
  -l python \
  -o ./python-client
