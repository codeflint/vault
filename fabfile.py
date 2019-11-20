from fabric.api import task, run, local, put

@task
def upload_app():
    dst = '/home/ubuntu/vault'

    run('sudo rm -rf %s' % dst)
    local("rm -f app.tar.gz; git ls-files > list_of_files; " +
          "find extern -type f | grep -v /.git >> list_of_files; " +
          "tar -zcf app.tar.gz -T list_of_files; rm list_of_files")

    run('mkdir -p %s' % dst)
    put('app.tar.gz', '%s/app.tar.gz' % dst)
    run('rm -rf app.tar.gz')
    run('cd %s/; tar -zxf %s/app.tar.gz' % (dst, dst))
    run('rm -rf  %s/app.tar.gz' % dst)
    # run('rm -rf  /home/ubuntu/docker_volumes/consul_data_bootstrap/*')
    # run('rm -rf  /home/ubuntu/docker_volumes/consul_data_0/*')
    # run('rm -rf  /home/ubuntu/docker_volumes/consul_data_1/*')
    # run('rm -rf  /home/ubuntu/docker_volumes/consul_data_2/*')
    local('rm -rf  app.tar.gz')
