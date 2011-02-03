AWS - Amazon Web Services
=========================

AWS cloud plugin provide "zero conf" discovery using ec2 and gateway based storage using s3. The plugin can be installed using **plugin -install cloud-aws**.


The cloud aws plugin provides the following services:


===============================================  ==================================
 Module                                           Description                      
===============================================  ==================================
:doc:`ec2_discovery <./ec2_discovery/index>`     "zero conf" discovery using ec2.  
:doc:`s3_gateway <./s3_gateway/index>`           s3 based gateway implementation.  
===============================================  ==================================

Region
------

The **cloud.aws.region** can be set to a region and will automatically use the relevant settings for both **ec2** and **s3**. The available values are: **us-east-1**, **us-west-1**, **ap-southeast-1**, **eu-west-1**.


