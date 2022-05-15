# Reboot AWS Instances

Esta é uma função lambda da AWS escrita em Python + Boto3 que tem como propósito reiniciar instâncias atreladas a um loadbalancer (ELB ou ELBv2) que estejam com sua saúde comprometida. Abaixo um diagrama ilustrando a arquitetura:

![](/home/stcruz/projetos/reboot-aws-instances/architecture.png)

Há um alarme configurado dentro do CloudWatch mensurando a quantidade média de *hosts* que apresentam problemas dentro do *loadbalancer*. Quando ativado, este alarme terá como *action* a publicação em um tópico SNS que terá como assinante a função lambda em questão que quando disparada receberá o evento do tópico informando o *loadbalancer* ou o *target group* e com esta informação em mãos, pesquisará qual ou quais instâncias apresentam problemas e realizará o *reboot*.

> Caso você esteja utilizando um ELB Classic, a métrica será diretamente sobre o *loadbalancer*. Caso seja um ELBv2, será sobre o *Target Group*.
